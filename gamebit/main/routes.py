from flask import Flask, Blueprint, render_template
from gamebit.models import User

main = Blueprint("main", __name__)

@main.route("/")
@main.route("/home")
def home():
  return render_template("home/home.html", title="Home")

@main.route("/about")
def about():
  users = User.query.all()
  return render_template("home/about.html", title="About us", users=users)

@main.route("/about/rules")
def rules():
  return render_template("home/rules.html", title="Rules")
