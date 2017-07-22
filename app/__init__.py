from flask import Flask
from flask.ext.moment import Moment
from flask.ext.mail import Mail
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.pagedown import PageDown

from config import config


mail = Mail()
boots = Bootstrap()
db = SQLAlchemy()
loginmanager = LoginManager()
moment = Moment()
pagedown = PageDown()

loginmanager.session_protection = 'strong'
loginmanager.login_view = 'auth.login'


def create_app(config_name):

    app = Flask(__name__)

    app.config.from_object(config[config_name])

    config[config_name].init_app(app)
    mail.init_app(app)
    boots.init_app(app)
    db.init_app(app)
    loginmanager.init_app(app)
    moment.init_app(app)
    pagedown.init_app(app)

    from .auth import auth
    from .main import main
    from .api_1_0 import api as api_1_0
    from .exam import exam

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(api_1_0, url_prefix='/api')
    app.register_blueprint(exam, url_prefix='/exam')

    return app