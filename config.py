# third-party imports
from flask import Flask
from flask_migrate import Migrate
from .models import *
from . import db

# db variable initialization

class Config(object):
    """
    Common configurations
    """

    # Put any configurations here that are common across all environments


class DevelopmentConfig(Config):
    """
    Development configurations
    """

    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/img_feed'


class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True, template_folder='templates')
    app.config.from_object(app_config[config_name])
    db.init_app(app)
    migrate = Migrate(app, db)
    return app
