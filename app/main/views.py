from datetime import datetime
from flask import render_template, abort, flash, make_response
from flask import current_app, redirect, url_for, request
from flask.ext.login import login_required, current_user

from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from ..decorator import permission_required, admin_required
from ..models import Permission, User, Role, Post, Comment, RandomWord, ForgettableWord
from .. import db


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()

    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post()

        post.body = form.body.data
        post.author = current_user._get_current_object()

        db.session.add(post)

        return redirect(url_for('main.index'))

    show_followed = False

    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))

    if show_followed:
        query = current_user.followed_post
    else:
        query = Post.query

    page = request.args.get('page', 1, type=int)

    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config.get('FLASKY_POST_PER_PAGE') or 3,
        error_out=False
    )

    posts = Post.query.order_by(Post.timestamp.desc()).all()

    posts = pagination.items

    return render_template('index.html', form=form, posts=posts,
                           pagination=pagination, show_followed=show_followed)


@main.route('/forgettablewords')
@login_required
def forgettablewords():
    page = request.args.get('page') or 1

    per_page = current_app.config.get('FLASK_WORDS_PER_PAGE') or 10

    pagination = current_user.forgeted_words.paginate(page, per_page=per_page,
                                                      error_out=False)

    words = pagination.items

    return render_template('forgettablewords.html',
                           words=words,
                           pagination=pagination,
                           endpoint='main.forgettablewords')


@main.route('/forgetword/<int:id>')
@login_required
def forgetword(word):
    word = RandomWord.query.get_or_404(id)

    word = ForgettableWord.query.filter_by(str=word.str).first()

    if word is None:
        word = ForgettableWord(str=word, count=1, user=current_user._get_current_object())
    else:
        word.count += 1

    db.session.add(word)
    db.session.commit()

    flash('happy to plus one')

    return redirect('main.randomwords', id=word.id)


@main.route('/randomwords/<int:id>')
@login_required
def randomwords(id):
    if id == 0:
        id = int(request.cookies.get('word_id') or 1)

    if id < 1 or id > RandomWord.query.count():
        abort(404)

    has_pre = True
    has_next = True

    if id == 1:
        has_pre = False

    elif id == RandomWord.query.count():
        has_next = False

    word = RandomWord.query.get_or_404(id)

    resp = make_response(render_template('randomwords.html',
                                         word=word.str, has_next=has_next,
                                         has_pre=has_pre, num=id))

    resp.set_cookie('word_id', str(id), max_age=30*24*60*60)

    return resp


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    post = comment.post

    comment.disabled = False

    db.session.add(comment)
    db.session.commit()

    return redirect(url_for('main.post', id=post.id,
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    post = comment.post

    comment.disabled = True

    db.session.add(comment)
    db.session.commit()

    return redirect(url_for('main.post', id=post.id,
                            page=request.args.get('page', 1, type=int)))


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)

    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)

    return resp


@main.route('/followed_by/<username>')
@login_required
def followed_by(username):
    user = User.query.filter_by(username=username).first()

    if user is None:
        abort(403)

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('FLASKY_FOLLOWED_PER_PAGE') or 3

    pagination = user.followed.paginate(
        page,
        per_page=per_page,
        error_out=False
    )

    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]

    return render_template('followers.html',
                           pagination=pagination,
                           endpoint='main.followed_by',
                           user=user,
                           follows=follows,
                           title='followed_by')


@main.route('/followers/<username>')
@login_required
def followers(username):
    user = User.query.filter_by(username=username).first()

    if user is None:
        abort(404)

    page = request.args.get('page', 1, type=int)

    pagination = user.followers.paginate(
        page,
        per_page=current_app.config.get('FLASKY_FOLLOWERS_PER_PAGE') or 3,
        error_out=False
    )

    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]

    return render_template('followers.html',
                           pagination=pagination,
                           endpoint='main.followers',
                           user=user,
                           follows=follows,
                           title='followers')


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()

    if user is None:
        abort(404)

    if not current_user.is_following(user):
        flash('You are not following this user now')

        return redirect(url_for('main.user', username=username))

    current_user.unfollow(user)

    flash('You are not following %s now' % (username))
    return redirect(url_for('main.user', username=username))


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()

    if user is None:
        abort(404)

    if current_user.is_following(user):
        flash('You are already following this user')

        return redirect(url_for('main.user', username=username))

    current_user.follow(user)

    flash('You are now following %s' % (username))

    return redirect(url_for('main.user', username=username))


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)

    if current_user != post.author and \
            not current_user.is_administrator():
        abort(403)

    form = PostForm()

    if form.validate_on_submit():
        post.body = form.body.data
        post.timestamp = datetime.utcnow()

        db.session.add(post)
        db.session.commit()

        return redirect(url_for('main.post', id=id))

    form.body.data = post.body

    return render_template('edit-post.html', form=form)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)

    form = CommentForm()

    if form.validate_on_submit():
        if current_user.can(Permission.COMMENT):
            comment = Comment(body=form.body.data, 
                              author=current_user._get_current_object(), 
                              post=Post.query.get_or_404(id))

            db.session.add(comment)
            db.session.commit()

            flash('You comment has been published')

            return redirect(url_for('main.post', id=id))
        else:
            abort(403)

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('FLASKY_COMMENT_PER_PAGE') or 3

    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=per_page, error_out=False
    )

    comments = pagination.items

    return render_template('post.html',
                           pagination=pagination,
                           endpoint='main.post',
                           posts=[post],
                           comments=comments,
                           form=form)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    posts = user.posts.order_by(Post.timestamp.desc()).all()

    if user is None:
        abort(404)

    return render_template('user.html', user=user, posts=posts)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data

        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('You profile has been updated')

        return redirect(url_for('main.edit_profile'))

    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me

    return render_template('edit-profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)

    form = EditProfileAdminForm(user)

    if form.validate_on_submit():
        user.e_mail = form.e_mail.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role_id.data)

        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data

        db.session.add(user)

        flash('The profile has been updated')

        return redirect(url_for('main.edit_profile_admin', id=id))

    form.e_mail.data = user.e_mail
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role_id.data = user.role_id

    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me

    return render_template('edit-profile.html', form=form)


@main.route('/admin')
@login_required
@admin_required
def admin():
    return 'for admin'


@main.route('/maderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderator():
    return 'for moderator'
