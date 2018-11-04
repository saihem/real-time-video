import os

from flask import Flask

from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True, template_folder='templates', static_url_path='/static')
    app.config.from_object(app_config[config_name])
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
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/img_feed'
    UPLOAD_FOLDER = '/path/to/the/uploads'


class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}




