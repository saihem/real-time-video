import os
from flask_sqlalchemy import SQLAlchemy
from .config import create_app
from flask_migrate import Migrate


config_name = os.getenv('FLASK_CONFIG')  # config name will be used in create_app
app = create_app('development')
db = SQLAlchemy(app=app)
db.init_app(app)
from .models import *
migrate = Migrate(app, db)
