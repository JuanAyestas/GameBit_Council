import os
from flask import (Flask, Blueprint, request, render_template, flash, 
                   redirect, url_for, abort, current_app)
from gamebit.models import Meme
from flask_login import current_user
from gamebit import db
from gamebit.memes.forms import MemeForm
from gamebit.users.utils import save_picture_all

memes = Blueprint("memes", __name__)

#meme routes
@memes.route("/memes", methods=["GET", "POST"])
def meme_list():
  page = request.args.get("page", 1, type=int)
  memes = Meme.query.order_by(
      Meme.date_posted.desc()).paginate(page=page, per_page=10)
  return render_template("memes/meme_list.html", title="Memes", memes=memes)


@memes.route("/memes/mem-<meme_id>", methods=["GET", "POST"])
def full_meme(meme_id):
  meme = Meme.query.get_or_404(meme_id)
  return render_template("memes/full_meme.html", title="{}".format(meme.caption), meme=meme)


@memes.route("/memes/new", methods=["GET", "POST"])
def new_meme():
  if current_user.is_authenticated:
    form = MemeForm()
    if form.validate_on_submit():
      if form.meme.data:
        posted_meme = save_picture_all(
            form.meme.data, current_app.config["MEME_PATH"], (1280, 720))
        meme = Meme(meme=posted_meme, caption=form.caption.data,
                    author=current_user)
        db.session.add(meme)
      db.session.commit()
      flash(f"Your meme has been submitted!", "success")
      return redirect(url_for("memes.meme_list"))
  else:
    abort(403)
  return render_template("memes/new_meme.html", title="New Meme", form=form, legend="Make someone laugh!")


@memes.route("/memes/delete/mem-<meme_id>", methods=["GET", "POST"])
def delete_meme(meme_id):
  meme = Meme.query.get_or_404(meme_id)
  if current_user == meme.author: 
    path = current_app.config["MEME_PATH"] + meme.meme
    try:
      if os.path.isfile(path):
        os.remove(path)
    except OSError as e:
      print("Error: {} : {}".format(
          current_app.config["REVIEW_PIC_PATH"], e.strerror))
    db.session.delete(meme)
    db.session.commit()
    flash('The picture has been deleted!', 'success')
    return redirect(url_for('memes.meme_list'))
  elif current_user.role == "Admin":
    path = current_app.config["MEME_PATH"] + meme.meme
    try:
      if os.path.isfile(path):
        os.remove(path)
    except OSError as e:
      print("Error: {} : {}".format(
          current_app.config["REVIEW_PIC_PATH"], e.strerror))
    db.session.delete(meme)
    db.session.commit()
    flash('The picture has been deleted!', 'success')
    return redirect(url_for('memes.meme_list'))
  else:
    abort(403)
