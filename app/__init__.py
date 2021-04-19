from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path
import os
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
from pathlib import Path

db = SQLAlchemy()
load_dotenv()
DB_NAME = "database.db"
oauth = OAuth()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{DB_NAME}'

    db.init_app(app)
    oauth.init_app(app)

    register_google(app)
    
    from .views import views
    from .auth import auth
    from .mail import mail

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(mail, url_prefix='/mail/')

    from .models import User, Messages, Receiver, Carboncopy
    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


    
def create_database(app):
    if not path.exists('app/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')


def register_google(app):
      oauth = OAuth(app)

def readFile(filename):
    filehandle = open(filename)
    print(filehandle.read())
    filehandle.close()