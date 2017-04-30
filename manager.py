from flask.ext.script import Shell
from flask.ext.script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import create_app
from app import db
from app.models import User, Food, Order, OrderDetail, Role, Post, RandomWord
from app.models import ForgettableWord


app = create_app('development')
manager = Manager(app)

migrate = Migrate(app, db)


def make_shell_context():
    return dict(
            app=app, db=db, Role=Role, User=User, Post=Post,
            Food=Food, Order=Order, OrderDetail=OrderDetail,
            RandomWord=RandomWord, ForgettableWord=ForgettableWord)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()