from flask import Flask
from celery import Celery

from snakeeyes.blueprints.page import page
from snakeeyes.blueprints.contact import contact
from snakeeyes.extensions import debug_toolbar, mail, csrf

CELERY_TASK_LIST = [
    'snakeeyes.blueprints.contact.tasks',
]

def create_celery_app(app=None):
    """
    Create a new Celery object and tie together the Celery config with the app's
    config. Wrap all tasks in the context of the application.

    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()

    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        include=CELERY_TASK_LIST
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return celery.Task.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

def create_app(settings_override=None):
    """
    Create a Flask application using the app factory pattern.

    :param settings_override: Override settings
    :return: Flask app
    """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object('config.settings')
    app.config.from_pyfile('settings.py', silent=True)

    if settings_override:
        app.config.update(settings_override)

    register_blueprints(app)
    init_extensions(app)

    return app

def register_blueprints(app):
    """
    Register blueprints with the app.

    :param app: Flask application instance
    :return: None
    """
    app.register_blueprint(page)
    app.register_blueprint(contact)

def init_extensions(app):
    """
    Initialize extensions and associate them with the app.

    :param app: Flask application instance
    :return: None
    """
    debug_toolbar.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
