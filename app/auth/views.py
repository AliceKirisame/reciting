from flask import render_template, request
from flask import redirect, url_for, flash
from flask.ext.login import login_user, logout_user, login_required
from flask.ext.login import current_user

from . import auth
from .forms import LoginForm, RegistrationForm

from ..models import User
from .. import db
from ..e_mail import send_email


@auth.route('/')
def index():
    return render_template('none.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():

    loginform = LoginForm()

    if loginform.validate_on_submit():

        user = User.query.filter_by(e_mail=loginform.e_mail.data).first()

        if user is not None and user.verify_password(loginform.password.data):
            login_user(user, loginform.remember_me.data)
            return redirect(url_for('main.index'))
        flash('invalid username or password')

    return render_template('auth/login.html', loginform=loginform)


@auth.route('/logout')
@login_required
def logout():

    logout_user()
    flash('you have been logged out')

    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():

    logout_user()

    registrationform = RegistrationForm()

    if registrationform.validate_on_submit():
        user = User(e_mail=registrationform.e_mail.data,
                    username=registrationform.username.data,
                    password=registrationform.password.data)

        db.session.add(user)
        db.session.commit()

        user.follow(user)

        token = user.generate_confirmation_token()

        send_email([user.e_mail], '账户确认测试', 'auth/email/confirm', token=token)

        flash('register successfully.Please login to confirm it')

        return redirect(url_for('auth.login'))

    return render_template(
        'auth/register.html',
        registrationform=registrationform
        )


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(
        [current_user.e_mail],
        'confirmed email',
        'auth/email/confirm',
        token=token)

    flash('A confirmation e_mail has been sent to your e_mail')

    return redirect(url_for('main.index'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))

    if current_user.confirm(token):
        flash('You have confirmed your account')
    else:
        flash('The confirmation link is invalid or has expired')

    return redirect(url_for('main.user', username=current_user.username))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()

        if not current_user.confirmed \
            and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
                    return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.confirmed or current_user.is_anonymous:
        return redirect(url_for('main.index'))

    return render_template('auth/email/unconfirmed.html')