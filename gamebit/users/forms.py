from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from gamebit.models import User, Review
from flask_login import current_user

class RegistrationForm(FlaskForm):
  username = StringField("Username",
                         validators=[DataRequired(), Length(min=2, max=20)])
  email = StringField("Email", validators=[DataRequired(), Email()])
  password = PasswordField("Password", validators=[
                           DataRequired(), Length(min=6)])
  confirm_password = PasswordField("Confirm Password",
                                   validators=[DataRequired(), EqualTo("password")])
  role = StringField("Role")
  submit = SubmitField("Sign up")

  def validate_email(self, email):
    user = User.query.filter_by(email=email.data).first()
    if user:
      raise ValidationError(
          "That email is already taken, please choose a different one.")

  def validate_username(self, username):
    user = User.query.filter_by(username=username.data).first()
    if user:
      raise ValidationError(
          "That username already is taken, please choose a different one.")

class LoginForm(FlaskForm):
  email = StringField("Email", validators=[DataRequired(
      "Don't leave your Email empty"), Email()])
  password = PasswordField("Password", validators=[
                           DataRequired("Don't leave your Password empty")])
  remember = BooleanField("Remember Me")
  submit = SubmitField("Log in")

class UserLoginForm(FlaskForm):
  username = StringField("Username", validators=[
                         DataRequired("Don't leave your Username empty")])
  password = PasswordField("Password", validators=[
                           DataRequired("Don't leave your Password empty")])
  remember = BooleanField("Remember Me")
  submit = SubmitField("Log in")

class UpdateAccountForm(FlaskForm):
  username = StringField("Username",
                         validators=[DataRequired(), Length(min=2, max=20)])
  email = StringField("Email", validators=[DataRequired(), Email()])
  picture = FileField("Change your profile picture", validators=[
                      FileAllowed(["jpg", "png", "gif", "bitmap", "jpeg"])])
  submit = SubmitField("Save Changes")

  def validate_email(self, email):
    if email.data != current_user.email:
      user = User.query.filter_by(email=email.data).first()
      if user:
        raise ValidationError(
            "That email is already taken, please choose a different one.")

  def validate_username(self, username):
    if username.data != current_user.username:
      user = User.query.filter_by(username=username.data).first()
      if user:
        raise ValidationError(
            "That username already is taken, please choose a different one.")

class RequestResetForm(FlaskForm):
  email = StringField("Email", validators=[DataRequired(
      "Don't leave your Email empty"), Email()])
  submit = SubmitField("Request Password Reset")

  def validate_email(self, email):
    user = User.query.filter_by(email=email.data).first()
    if user is None:
      raise ValidationError(
          "That account doesn't exist. Please choose a different one or register.")

class ResetPasswordForm(FlaskForm):
  password = PasswordField("Password", validators=[
                           DataRequired(), Length(min=6)])
  confirm_password = PasswordField("Confirm Password",
                                   validators=[DataRequired(), EqualTo("password")])
  submit = SubmitField("Reset Password")
