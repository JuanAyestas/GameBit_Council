from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_admin import Admin
import yagmail
from gamebit.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"
yag = yagmail.SMTP('gamebitpage@gmail.com')

from gamebit.users.utils import AdminView, UserModelView
from gamebit.models import User, Review, Meme

admin = Admin(index_view=AdminView())
admin.add_view(UserModelView(User, db.session))
admin.add_view(UserModelView(Review, db.session))
admin.add_view(UserModelView(Meme, db.session))

def create_app(config_class=Config):
  app = Flask(__name__)
  app.config.from_object(Config)

  db.init_app(app)
  bcrypt.init_app(app)
  login_manager.init_app(app)
  admin.init_app(app)
  
  from gamebit.users.routes import users
  app.register_blueprint(users)
  from gamebit.reviews.routes import reviews
  app.register_blueprint(reviews)
  from gamebit.memes.routes import memes
  app.register_blueprint(memes)
  from gamebit.main.routes import main
  app.register_blueprint(main)
  from gamebit.errors.handlers import errors
  app.register_blueprint(errors)
  
  return app

