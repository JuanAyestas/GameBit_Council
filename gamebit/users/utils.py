import os
import secrets
from PIL import Image
from flask import url_for, redirect, request, current_app
from gamebit import yag
from flask_login import current_user
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView

class UserModelView(ModelView):
  def is_accessible(self):
    return (current_user.is_authenticated and current_user.role == "Admin" and
            current_user.username == "Kuro Cato"
            or current_user.is_authenticated and current_user.role == "Admin" and
            current_user.username == "NecroSatan")

  def inaccessible_callback(self, name, **kwargs):
    return redirect(url_for("main.home", next=request.url))


class AdminView(AdminIndexView):
  def is_accessible(self):
    return current_user.is_authenticated and current_user.role == "Admin"

  def inaccessible_callback(self, name, **kwargs):
    return redirect(url_for("main.home", next=request.url))


def send_reset_email(user):
  token = user.get_reset_token()
  to = [user.email]
  subject = "Password Reset Request"
  img = "./static/profile_pictures/unnamed.jpg"
  body = f"""To reset your password, visit the following link:
  {url_for('reset_token', token=token, _external=True)}

  If you didn't make this request, simply ignore and there won't be changes, but you may want to check your account info."""
  yag.send(to, subject, [body, img])


def save_picture_all(form_picture, save_path, size):
  random_hex = secrets.token_hex(8)
  file_name, file_ext = os.path.splitext(form_picture.filename)
  picture_filename = random_hex + file_ext
  picture_path = os.path.join(
      current_app.root_path, save_path, picture_filename)

  output_size = (size)
  image = Image.open(form_picture)
  image.thumbnail(output_size)
  image.save(picture_path)

  return picture_filename
