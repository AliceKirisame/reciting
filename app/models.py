import bleach
from datetime import datetime
from flask import g, current_app
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import db, loginmanager

from .exceptions import ValidationError


class TmpWord(db.Model):
    __tablename__ = 'tmpwords'

    id = db.Column(db.Integer, primary_key=True)
    str = db.Column(db.String(64))


class InputWord(db.Model):
    __tablename__ = 'inputwords'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(64))
    group = db.Column(db.Integer)
    meaning = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Iteration1(db.Model):
    __tablename__ = 'one'

    id = db.Column(db.Integer, primary_key=True)
    str = db.Column(db.String(64))
    count = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Iteration2(db.Model):
    __tablename__ = 'two'

    id = db.Column(db.Integer, primary_key=True)
    str = db.Column(db.String(64))
    count = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Iteration3(db.Model):
    __tablename__ = 'more'

    id = db.Column(db.Integer, primary_key=True)
    str = db.Column(db.String(64))
    count = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class ForgettableWord(db.Model):
    __tablename__ = 'forgettablewords'

    id = db.Column(db.Integer, primary_key=True)
    str = db.Column(db.String(64))
    count = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class RandomWord(db.Model):
    __tablename__ = 'randomwords'

    id = db.Column(db.Integer, primary_key=True)
    str = db.Column(db.String(64))

    @staticmethod
    def insert_words():
        words = open('1.txt', mode='r')
        if words is None:
            print('error')
            return False

        for word in words:
            word = word.strip('\n')
            w = RandomWord(str=word)
            db.session.add(w)
            db.session.commit()


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    disabled = db.Column(db.Boolean, default=False)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))


class Follow(db.Model):
    __tablename__ = 'follows'

    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']

        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, out_format='html'),
            allowed_tags, strip=True
        ))

    @staticmethod
    def generate_fake(count=100):
        for i in range(count):
            from random import seed, randint
            import forgery_py

            seed()
            user_count = User.query.count()

            u = User.query.offset(randint(0, user_count-1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                     timestamp=forgery_py.date.date(True),
                     author=u)

            db.session.add(p)
            db.session.commit()


db.event.listen(Post.body, 'set', Post.on_changed_body)


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):

    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    rolename = db.Column(db.String(64), unique=True)
    Permissions = db.Column(db.Integer)
    default = db.Column(db.Boolean, default=False, index=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (
                Permission.FOLLOW | Permission.COMMENT |
                Permission.WRITE_ARTICLES,
                True),

            'Mederator': (
                Permission.FOLLOW | Permission.COMMENT |
                Permission.WRITE_ARTICLES | Permission.MODERATE_COMMENTS,
                False),

            'Administrator': (
                0xff,
                False),

        }

        for r in roles:
            role = Role.query.filter_by(rolename=r).first()

            if role is None:
                role = Role(rolename=r)
                role.Permissions = roles[r][0]
                role.default = roles[r][1]

                db.session.add(role)

            db.session.commit()


class AnonymousUser(AnonymousUserMixin):
    def can(self, Permissions):
        return False

    def is_administrator(self):
        return False


class User(UserMixin, db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    e_mail = db.Column(db.String(64), unique=True)
    username = db.Column(db.String(64), unique=True)
    wxid = db.Column(db.String(64))
    status = db.Column(db.Integer)
    password_hash = db.Column(db.String(128))
    lastorder = db.Column(db.Integer)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)

    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    posts = db.relationship('Post', backref='author', lazy='dynamic')

    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')

    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    forgeted_words = db.relationship('ForgettableWord', backref='user',
                                     lazy='dynamic')

    iteration1 = db.relationship('Iteration1', backref='user',
                                 lazy='dynamic')

    iteration2 = db.relationship('Iteration2', backref='user',
                                 lazy='dynamic')

    iteration3 = db.relationship('Iteration3', backref='user',
                                 lazy='dynamic')


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

        if self.role is None:
            if self.e_mail == current_app.config['MAIL_USERNAME']:
                self.role = Role.query.filter_by(Permissions=0xff).first()
            else:
                self.role = Role.query.filter_by(default=True).first()

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token)
        except:
            return False

        if data.get('confirm') != self.id:
            return False

        self.confirmed = True
        db.session.add(self)
        return True

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, Permissions):
        return self.role is not None \
            and (self.role.Permissions & Permissions) == Permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(e_mail=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()

            except IntegrityError:
                db.session.rollback()

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
            db.session.commit()

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()

        if f:
            db.session.delete(f)

    @property
    def followed_post(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id) \
            .filter(Follow.follower_id == self.id)

    orders = db.relationship('Order', backref='user')

    def to_json(self):

        json_user = {
            'id': self.id,
            'username': self.username
        }

        return json_user

    @staticmethod
    def from_json(json_user):
        e_mail = json_user.get('e_mail')
        if e_mail is None or e_mail == '':
            raise ValidationError('User does not have a e_mail')

        username = json_user.get('username')
        if username is None or username == '':
            raise ValidationError('User does not have a username')

        password = json_user.get('password')
        if password is None or password == '':
            raise ValidationError('User does not have a password')

        if User.query.filter_by(username=username).first():
            raise ValidationError('Username already registered.')

        if User.query.filter_by(e_mail=e_mail).first():
            raise ValidationError('Email already registered.')

        return User(e_mail=e_mail, username=username, password=password)


class Food(db.Model):

    __tablename__ = 'foods'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    price = db.Column(db.Integer)

    @staticmethod
    def to_json():
        foods = Food.query.all()

        foods_json = {'count': len(foods)}

        for i in range(len(foods)):
            foods_json[str(i)] = {
                                'id': str(foods[i].id), 'name': foods[i].name,
                                'price': str(foods[i].price)
                                }

#        for i in range(len(foods)):
#           for key in foods[i]:
#               foods_json[str(i)][str(key)] = foods[i][key]

        return foods_json


class Order(db.Model):

    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    details = db.relationship('OrderDetail', backref='order')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    confirmed = db.Column(db.Integer)

    @staticmethod
    def from_json(json_order):
        user = g.current_user
        details = []

        if user is None:
            raise ValidationError('login required')

#        details = json_order.get('details')
#        if details is None:
#            raise ValidationError('Order does not have details')

        str_count = json_order.get('count')
        if str_count is None:
            raise ValidationError('the num of foods is invalid')

        count = int(str_count)
        if count <= 0:
            raise ValidationError('the num of foods is invalid')

        for i in range(count):
            if json_order.get(str(i)) is None:
                raise ValidationError('order error occured')

            details.append(json_order.get(str(i)))

        return Order(user_id=user.id), details


class OrderDetail(db.Model):

    __tablename__ = 'details'
    id = db.Column(db.Integer, primary_key=True)

    food_id = db.Column(db.Integer, db.ForeignKey('foods.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))

    @staticmethod
    def from_json(json_detail):

        return OrderDetail(
            food_id=json_detail.get('food_id'),
            order=json_detail.get('order_id'))


@loginmanager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


loginmanager.anonymous_user = AnonymousUser
