from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, SubmitField
from wtforms import BooleanField, SelectField
from wtforms.validators import Length, Required, Email, Regexp
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField

from ..models import Role, User


class CommentForm(Form):
    body = StringField('Enter your comment', validators=[Required()])
    submit = SubmitField('submit')


class PostForm(Form):
    body = PageDownField("What's in your mind?", validators=[Required()])
    submit = SubmitField('submit')


class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('Talk someting')
    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):
    e_mail = StringField('E-mail', validators=[
                                    Required(), 
                                    Length(1, 64), 
                                    Email()
                                        ])

    username = StringField('Username', validators=[
                        Required(), Length(1, 64),
                        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                               'username must have only letters,numbers,'
                               'dots or underscores')
                                    ])

    confirmed = BooleanField('Confirmed')

    role_id = SelectField('role_id', coerce=int)

    name = StringField('Real Name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About Me')

    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)

        self.user = user
        self.role_id.choices = [
                        (role.id, role.rolename)
                        for role in Role.query.order_by(Role.rolename).all()
                            ]

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in used')

    def validate_e_mail(self, field):
        if field.data != self.user.e_mail and \
                User.query.filter_by(e_mail=field.data).first():
            raise ValidationError('Email already registered')