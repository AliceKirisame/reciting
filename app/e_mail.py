from threading import Thread

from flask import render_template, current_app
from flask_mail import Message

from . import mail


def send_async_email(app, msg): 
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()

    msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=to)

    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)

    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


def quick_send():
    send_email(['alicekirisame@163.com'], 'test', 'auth/email/test', token='test')
