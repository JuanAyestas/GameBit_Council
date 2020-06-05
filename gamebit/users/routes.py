import os
from flask import (Flask, Blueprint, redirect, url_for, render_template, 
                   flash, abort, request, current_app)
from flask_login import current_user, login_user, logout_user, login_required
from gamebit.users.forms import (RegistrationForm, LoginForm, UserLoginForm, 
                                 UpdateAccountForm, RequestResetForm, ResetPasswordForm)
from gamebit.models import User, Review
from gamebit import bcrypt, db
from gamebit.users.utils import send_reset_email, save_picture_all

users = Blueprint("users", __name__)

@users.route("/register", methods=["GET", "POST"])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('main.home'))
  form = RegistrationForm()
  if form.validate_on_submit():
    hashed_password = bcrypt.generate_password_hash(
        form.password.data).decode("utf-8")
    user = User(username=form.username.data,
                email=form.email.data, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    flash(f"Account successfully created!", "success")
    return redirect(url_for('users.login'))
  return render_template("users/visitor_register.html", title="Register", form=form, legend="Register Page")


@users.route("/register/staff/4NbsBs-zKQASnZwfcp0YPPVPks5G5qNCeBXqNAQewU1HbyUCykcWpSv0sxqrPeuUwXKcn8ZsfjUqx4M_zEGUh1ifOKj4m4xR4cBQqZmMYWV9Vjf6BdlJmmt2qPC9z3rcL9mdyyxdn8L74f1vdnXyyP58LKLBTBm7", methods=["GET", "POST"])
def staff_register():
  if current_user.is_authenticated:
    return redirect(url_for('main.home'))
  form = RegistrationForm()
  if form.validate_on_submit():
    hashed_password = bcrypt.generate_password_hash(
        form.password.data).decode("utf-8")
    user = User(username=form.username.data, role="Admin",
                email=form.email.data, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    flash(f"Account successfully created!", "success")
    return redirect(url_for('users.login'))
  return render_template("users/staff_register.html", title="Staff Register", form=form, legend="Register Page")


@users.route("/login/email", methods=["GET", "POST"])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('main.home'))
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    if user and bcrypt.check_password_hash(user.password, form.password.data):
      login_user(user, remember=form.remember.data)
      next_page = request.args.get("next")
      flash(f"You've logged in successfully!", "success")
      return redirect(next_page) if next_page else redirect(url_for('main.home'))
    else:
      flash(f"Failed to log in. Please check the email and password.", "danger")
  return render_template("users/login.html", title="Login", form=form, legend="Login Page")


@users.route("/login/user", methods=["GET", "POST"])
def user_login():
  if current_user.is_authenticated:
    return redirect(url_for('main.home'))
  form = UserLoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(username=form.username.data).first()
    if user and bcrypt.check_password_hash(user.password, form.password.data):
      login_user(user, remember=form.remember.data)
      next_page = request.args.get("next")
      flash(f"You've logged in successfully!", "success")
      return redirect(next_page) if next_page else redirect(url_for('main.home'))
    else:
      flash(f"Failed to log in. Please check the username and password.", "danger")
  return render_template("users/user_login.html", title="Login", form=form, legend="Login Page")


@users.route("/logout")
def logout():
  logout_user()
  flash(f"You've successfully logged off!", "success")
  return redirect(url_for("main.home"))


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
  reviews = Review.query.filter_by(author=current_user)
  form = UpdateAccountForm()
  if form.validate_on_submit():
    if form.picture.data:
      path = current_app.config["PROFILE_PIC_PATH"]
      try:
        if not os.path.exists(path):
          os.mkdir(path)
      except OSError:
        print("Couldn't create the directory {}".format(path))
      picture_file = save_picture_all(form.picture.data, path, (400, 225))
      current_user.profile_picture = picture_file
    current_user.username = form.username.data
    current_user.email = form.email.data
    db.session.commit()
    flash(f"Your account info has been updated", "success")
    return redirect(url_for("users.account"))
  elif request.method == "GET":
    form.username.data = current_user.username
    form.email.data = current_user.email
  return render_template("users/account.html", title="Account Info", form=form,
                         legend="Account Info", reviews=reviews)


@users.route("/account/<int:user_id>", methods=['GET', 'POST'])
@login_required
def delete_account(user_id):
  user = User.query.get_or_404(user_id)
  if user != current_user:
    abort(403)
  logout_user()
  path_rem = current_app.config["PROFILE_PIC_PATH"] + user.profile_picture
  try:
    if os.path.isfile(path_rem):
      os.remove(path_rem)
  except OSError as e:
    print("Error: {} : {}".format(path_rem, e.strerror))
  db.session.delete(user)
  db.session.commit()
  flash('The user has been deleted!', 'success')
  return redirect(url_for('main.home'))


@users.route("/login/reset", methods=["GET", "POST"])
def reset_request():
  if current_user.is_authenticated:
    return redirect(url_for("main.home"))
  form = RequestResetForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    send_reset_email(user)
    flash(f"An Email has been sent with instructions to reset your password.", "info")
    return redirect(url_for("users.login"))
  return render_template("users/reset_request.html", title="Reset Password",
                         form=form, legend="Password Reset")


@users.route("/login/reset/<token>", methods=["GET", "POST"])
def reset_token(token):
  if current_user.is_authenticated:
    return redirect(url_for("main.home"))
  user = User.verify_token(token)
  if user is None:
    flash(f"That's an invalid or expired token", "warning")
    return redirect(url_for("users.reset_request"))
  form = ResetPasswordForm()
  if form.validate_on_submit():
    hashed_password = bcrypt.generate_password_hash(
        form.password.data).decode("utf-8")
    user.password = hashed_password
    db.session.commit()
    flash(f"Your password has been updated!", "success")
    return redirect(url_for('users.login'))
  return render_template("users/reset_token.html", title="Reset Password",
                         form=form, legend="Password Reset")
