import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = "condenserr.db"

#Logging Setup
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('condenserr_debug.log', mode='a')
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates', static_url_path='/')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .discord import discord
    from .backend import backend

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(backend, url_prefix='/')
    app.register_blueprint(discord, url_prefix='/')

    from .models import Item, Episode, Test

    with app.app_context():
        db.create_all()

    return app