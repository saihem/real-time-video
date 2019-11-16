import os

from flask import Flask


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True, template_folder='templates', static_url_path='/static')
    app.config.from_object(app_config[config_name])
    app.secret_key = 'my unobvious secret key'
    return app


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
    SQLALCHEMY_DATABASE_URI = ''
    UPLOAD_FOLDER = 'images/uploaded'
    SESSION_TYPE = 'filesystem'


class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}




