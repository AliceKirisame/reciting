from flask import render_template
from . import main


@main.app_errorhandler(400)
def bad_request(e):
    return render_template('errors/400.html')


@main.app_errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html')


@main.app_errorhandler(404)
def not_found(e):
    return render_template('errors/404.html')


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html')