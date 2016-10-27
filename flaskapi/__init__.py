from functools import wraps
from logging import DEBUG
from logging import ERROR
from logging import Formatter
from logging.handlers import SMTPHandler
from logging.handlers import WatchedFileHandler
import os

import click
from flask import Flask
from flask import jsonify
from flask import g
from flask import abort
from flask_cors import CORS
from werkzeug.contrib.cache import SimpleCache
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import InternalServerError


MAIL_LOG_FORMAT = """
Error:     %(levelname)s
Location:  %(pathname)s line %(lineno)d
Function:  %(module)s.%(funcName)s
Time:      %(asctime)s

%(message)s
"""


DEBUG_LOG_FORMAT = """
%(asctime)s - %(levelname)s - %(pathname)s - %(module)s.%(funcName)s
%(message)s
"""


def create_app(config=None):
    app = Flask(__name__)

    app.config.from_object('flaskapi.config')
    if isinstance(config, dict):
        app.config.update(**config)

    app.config.setdefault('CACHE_SECONDS', 604800)
    app.cache = SimpleCache(threshold=10, default_timeout=app.config['CACHE_SECONDS'])
    app.debug_log_format = DEBUG_LOG_FORMAT.strip()
    app.mail_log_format = MAIL_LOG_FORMAT.strip()

    configure_authentication(app)
    configure_error_handlers(app)
    configure_extensions(app)
    configure_views(app)
    configure_commands(app)

    if not app.debug:
        configure_logging(app)

    if app.debug:
        CORS(app)

    return app


def configure_logging(app):
    # Send WARNING messages to a file log.
    os.makedirs(os.path.dirname(app.config['LOG_FILE']), exist_ok=True)
    file_handler = WatchedFileHandler(filename=app.config['LOG_FILE'])
    file_handler.setLevel(DEBUG)
    file_handler.setFormatter(Formatter(app.debug_log_format, '%Y-%m-%d %H:%M:%S'))
    app.logger.addHandler(file_handler)

    # Send ERROR messages via email.
    mail_handler = SMTPHandler(
        (app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
        app.config['MAIL_FROM_ADDRESS'],
        app.config['ADMINS'],
        app.config['MAIL_ERROR_SUBJECT'])
    mail_handler.setLevel(ERROR)
    mail_handler.setFormatter(Formatter(app.mail_log_format, '%Y-%m-%d %H:%M:%S'))
    app.logger.addHandler(mail_handler)


def configure_error_handlers(app):
    def error_handler(exc):
        if not isinstance(exc, HTTPException):
            exc = InternalServerError()
        return jsonify(code=exc.code, message=exc.name), exc.code

    for code in default_exceptions.keys():
        app.register_error_handler(code, error_handler)


def configure_extensions(app):
    from flaskapi.ext import db
    from flaskapi.ext import mail

    db.init_app(app)
    mail.init_app(app)


def configure_views(app):
    from flaskapi.views import public
    from flaskapi.views import admin

    app.register_blueprint(admin.api, url_prefix='/admin')
    app.register_blueprint(public.api, url_prefix='/api')


def configure_authentication(app):
    from flaskapi.ext import auth
    from flaskapi.models import User

    @auth.verify_password
    def authenticate(username, password):
        user = User.select().filter(username=username).first()
        if user and (user.check_api_key(password) or user.check_password(password)):
            g.user = user
            return True
        return False

    @auth.error_handler
    def unauthorized():
        abort(401)

    # Monkeypatch the admin_required decorator onto the auth class.

    def admin_required(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            if not hasattr(g, 'user') or not getattr(g.user, 'is_admin', False):
                abort(401)
            return func(*args, **kwargs)
        return decorated

    auth.admin_required = admin_required


def configure_commands(app):
    @app.cli.command()
    def createadmin():
        """Create an admin user."""
        from flaskapi.models import User

        while True:
            username = click.prompt('Username')
            if not User.select().filter(username=username).first():
                break
            click.echo('Username already exists. Try again.')

        email = click.prompt('E-mail')

        while True:
            password = click.prompt('Password', hide_input=True)
            password_confirm = click.prompt('Password (confirm)', hide_input=True)
            if password == password_confirm:
                break
            click.echo('Passwords did not match. Try again.')

        User.create(username=username, email=email, password=password, is_admin=True)
        click.echo('User created successfully.')

    @app.cli.command()
    def routes():
        """List all routes."""
        rule_len = max(len(rule.rule) for rule in app.url_map.iter_rules()) + 3
        endp_len = max(len(rule.endpoint) for rule in app.url_map.iter_rules()) + 3

        line_str = '{:' + str(rule_len) + 's}{:' + str(endp_len) + '}{}'

        def get_output():
            for rule in app.url_map.iter_rules():
                methods = set(rule.methods) - {'HEAD', 'OPTIONS'}
                line_fmt = (rule.rule, rule.endpoint, ','.join(sorted(methods)))
                line = line_str.format(*line_fmt)
                yield line

        for line in sorted(get_output()):
            print(line)
