import os
from flask import (Flask, Blueprint, request, render_template, abort, flash, 
                   redirect, url_for, current_app)
from gamebit.models import Review, User, Meme, Picture
from flask_login import current_user, login_required
from gamebit import db
from gamebit.reviews.forms import ReviewForm, UpdateReviewForm, PictureReviewForm
from gamebit.users.utils import save_picture_all

reviews = Blueprint("reviews", __name__)

#Review routes
@reviews.route("/reviews")
def review_list():
  page = request.args.get("page", 1, type=int)
  reviews = Review.query.order_by(
      Review.date_posted.desc()).paginate(page=page, per_page=4)
  return render_template("reviews/review_list.html", title="Reviews", reviews=reviews)

@reviews.route("/reviews/summary/<string:username>")
def user_review(username):
  user = User.query.filter_by(username=username).first_or_404()
  reviews = Review.query.filter_by(author=user)
  memes = Meme.query.filter_by(author=user)
  if user.role == "Admin":
    return render_template("reviews/user_review.html", user=user, reviews=reviews,
                           memes=memes, title="Staff Summary")
  else:
    return render_template("reviews/user_review.html", user=user, reviews=reviews,
                           memes=memes, title="Visitor Summary")


@reviews.route("/reviews/new", methods=["GET", "POST"])
@login_required
def new_review():
  if current_user.role != "Admin":
    abort(403)
  form = ReviewForm()
  if form.validate_on_submit():
    if form.thumbnail.data:
      picture_thumbnail = save_picture_all(
          form.thumbnail.data, current_app.config["THUMBNAIL_PIC_PATH"], (1280, 720))
    review = Review(title=form.title.data, platform=form.platform.data, summary=form.summary.data,
                    content=form.content.data, author=current_user, thumbnail=picture_thumbnail)
    db.session.add(review)
    db.session.commit()
    flash(f"Your review has been submitted!", "success")
    return redirect(url_for("reviews.review_list"))
  return render_template("reviews/new_review.html", title="New Review", form=form,
                         legend="GameBit Review")


@reviews.route("/reviews/rev-<int:review_id>/uploads", methods=["GET", "POST"])
@login_required
def picture_upload(review_id):
  review = Review.query.get_or_404(review_id)
  if review.author != current_user and current_user.role != "Admin":
    abort(403)
  form = PictureReviewForm()
  if form.validate_on_submit and "pictures" in request.files:
    for picture in request.files.getlist("pictures"):
      picture_file = save_picture_all(
          picture, current_app.config["REVIEW_PIC_PATH"], (1600, 900))
      picture = Picture(picture_file=picture_file, review_id=review_id)
      db.session.add(picture)
    db.session.commit()
    flash(f"Your pictures have been submitted!", "success")
    return redirect(url_for("reviews.full_review", review_id=review_id))
  return render_template("reviews/reviews_upload.html", form=form, title="Upload Pictures",
                         review=review, legend="Uploading pictures for: {}".format(review.title))


@reviews.route("/reviews/rev-<int:review_id>", methods=["GET", "POST"])
def full_review(review_id):
  review = Review.query.get_or_404(review_id)
  pictures = Picture.query.filter_by(review_id=review_id)
  return render_template("reviews/full_review.html", title=review.title, review=review,
                         pictures=pictures)


@reviews.route("/reviews/rev-<int:review_id>/gallery", methods=["GET", "POST"])
def review_gallery(review_id):
  review = Review.query.get_or_404(review_id)
  pictures = Picture.query.filter_by(review_id=review_id)
  return render_template("reviews/review_gallery.html", title="{} - gallery".format(review.title),
                         review=review, pictures=pictures)


@reviews.route("/reviews/rev-<int:review_id>/gallery/pic-thumbnail", methods=["GET", "POST"])
def full_thumbnail(review_id):
  review = Review.query.get_or_404(review_id)
  return render_template("reviews/full_thumbnail.html", title="Full picture", review=review)


@reviews.route("/reviews/rev-<int:review_id>/gallery/pic-<int:picture_id>", methods=["GET", "POST"])
def full_picture(picture_id, review_id):
  review = Review.query.get_or_404(review_id)
  picture = Picture.query.get_or_404(picture_id)
  return render_template("reviews/full_picture.html", title="Full picture", picture=picture, review=review)


@reviews.route("/reviews/rev-<int:review_id>/gallery/pic-<int:picture_id>/delete", methods=["GET", "POST"])
def delete_picture(picture_id, review_id):
  review = Review.query.get_or_404(review_id)
  if review.author != current_user and current_user.role != "Admin":
    abort(403)
  picture = Picture.query.get_or_404(picture_id)
  path = current_app.config["REVIEW_PIC_PATH"] = "static/review_pictures/" + \
      picture.picture_file
  db.session.delete(picture)
  try:
    if os.path.isfile(path):
      os.remove(path)
  except OSError as e:
    print("Error: {} : {}".format(
        current_app.config["REVIEW_PIC_PATH"], e.strerror))
  db.session.delete(picture)
  db.session.commit()
  flash('The picture has been deleted!', 'success')
  return redirect(url_for('reviews.review_gallery', review_id=review.id))


@reviews.route("/reviews/rev-<int:review_id>/list", methods=["GET", "POST"])
@login_required
def edit_review(review_id):
  review = Review.query.get_or_404(review_id)
  if review.author != current_user and current_user.role != "Admin":
    abort(403)
  form = UpdateReviewForm()
  if form.validate_on_submit():
    if form.thumbnail.data:
      path = current_app.config["REVIEW_PIC_PATH"] = "static/thumbnail/" + \
          review.thumbnail
      try:
        if os.path.isfile(path):
          os.remove(path)
      except OSError as e:
        print("Error: {} : {}".format(
            current_app.config["REVIEW_PIC_PATH"], e.strerror))
      picture_thumbnail = save_picture_all(
          form.thumbnail.data, current_app.config["THUMBNAIL_PIC_PATH"], (1280, 720))
      review.thumbnail = picture_thumbnail
    review.title = form.title.data
    review.platform = form.platform.data
    review.summary = form.summary.data
    review.content = form.content.data
    db.session.commit()
    flash(f"Your review has been updated!", "success")
    return redirect(url_for("reviews.full_review", review_id=review.id))
  elif request.method == "GET":
    form.title.data = review.title
    form.platform.data = review.platform
    form.summary.data = review.summary
    form.content.data = review.content
    form.thumbnail.data = review.thumbnail
  return render_template("reviews/edit_review.html", title="Editing: {}".format(review.title),
                         review=review, form=form, legend="Update the review")


@reviews.route("/reviews/rev-<int:review_id>/delete", methods=["GET", "POST"])
@login_required
def delete_review(review_id):
  review = Review.query.get_or_404(review_id)
  if review.author != current_user and current_user.role != "Admin":
    abort(403)
  pictures = Picture.query.filter_by(review_id=review_id)
  for picture in pictures:
    path = current_app.config["REVIEW_PIC_PATH"] = "static/review_pictures/" + \
        picture.picture_file
    db.session.delete(picture)
    try:
      if os.path.isfile(path):
        os.remove(path)
    except OSError as e:
      print("Error: {} : {}".format(
          current_app.config["REVIEW_PIC_PATH"], e.strerror))
  db.session.delete(review)
  db.session.commit()
  flash('The review has been deleted!', 'success')
  return redirect(url_for('reviews.review_list'))
