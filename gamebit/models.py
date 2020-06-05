from flask import current_app
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from gamebit import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  profile_picture = db.Column(db.String(20), nullable=False, default="default.jpg")
  password = db.Column(db.String(60), nullable=False)
  active = db.Column(db.Boolean, default=True)
  role = db.Column(db.String(20), nullable=False, default="Visitor")
  confirmed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  
  review = db.relationship("Review", backref="author", lazy=True)
  
  meme = db.relationship("Meme", backref="author", lazy=True)
  
  def get_reset_token(self, expires_sec=1800):
    s = Serializer(current_app.config["SECRET_KEY"], expires_sec)
    return s.dumps({"user_id": self.id}).decode("utf-8")

  @staticmethod
  def verify_token(token):
    s = Serializer(current_app.config["SECRET_KEY"])
    try:
      user_id = s.loads(token)["user_id"]
    except:
      return None
    return User.query.get(user_id)
  
  def __repr__(self):
    return f"User('{self.username}', '{self.email}, '{self.profile_picture}')"


class Review(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100), unique=True, nullable=False)
  platform = db.Column(db.String(100), nullable=False)
  summary = db.Column(db.Text, nullable=False)
  content = db.Column(db.Text, nullable=False)
  thumbnail = db.Column(db.String(20), nullable=False)
  date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

  user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

  picture_id = db.relationship("Picture", backref="review", lazy=True)
  
  def __repr__(self):
    return f"Review ('{self.title}', '{self.platform}, '{self.date_posted}')"

class Meme(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  caption = db.Column(db.String(255), nullable=False)
  meme = db.Column(db.String(500), nullable=False)
  date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  # relationship with user
  user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class Picture(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  picture_file = db.Column(db.String(500), nullable=False)
  # relationship with review
  review_id = db.Column(
      db.Integer, db.ForeignKey('review.id'), nullable=False)
