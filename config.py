import os
from flask.ext.sqlalchemy import sqlalchemy


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'alicekirisame@163.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or '8pk9ks'
    MAIL_PORT = 25
    MAIL_SERVER = 'smtp.163.com'
    MAIL_USE_TLS = True

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'asdf'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    def init_app(app):
        pass
    

class DevelopmentConfig(Config):

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        'mysql+pymysql://root:8pk9ks@localhost/web'


config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}