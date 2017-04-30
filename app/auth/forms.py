from flask.ext.wtf import Form

from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from wtforms import ValidationError

from ..models import User


class NameForm(Form):

    username = StringField('Username', validators=[Required()])
    submit = SubmitField('submit')


class LoginForm(Form):
    e_mail = StringField(
        'e-mail', 
        validators=[Required(), Email(), Length(1, 64)])

    password = PasswordField('password', validators=[Required()])
    remember_me = BooleanField('remember me')
    submit = SubmitField('log in')


class RegistrationForm(Form):
    e_mail = StringField(
        'E-mail',
        validators=[Required(), Email(), Length(1, 64)])

    username = StringField(
            'Username', validators=[
                    Required(),
                    Length(1, 64),
                    Regexp('^[A-Za-z][A-Za-z0-9_]*$', 0, 'Invalidate Username')
                        ]
                    )

    password = PasswordField('Password', validators=[
                        Required(),
                        EqualTo('password2', message='Password does not match')
                            ]
                        )

    password2 = PasswordField('Confirm Password', validators=[Required()])

    submit = SubmitField('submit')

    def validate_e_mail(self, field):
        if User.query.filter_by(e_mail=field.data).first():
            raise ValidationError('email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('username already registerd.')