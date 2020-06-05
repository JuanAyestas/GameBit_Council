from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError
from gamebit.models import User, Review

class ReviewForm(FlaskForm):
  title = StringField("Title of the Game",
                      validators=[DataRequired("You can't leave the review without a title."), Length(min=4)])
  platform = StringField("Platforms where the game's available",
                         validators=[DataRequired("You can't leave the game without knowing where you can play it."), Length(min=4)])
  summary = TextAreaField("Short description about the game, it's genre and stuff like that",
                          validators=[DataRequired("Don't forget to add a short description, so they know what's going on."), Length(min=10)])
  content = TextAreaField("Actual content of the review",
                          validators=[DataRequired("A review without a review? You can't leave this section empty"), Length(min=20)])
  thumbnail = FileField("Upload a thumbnail for the Review",
                        validators=[FileAllowed(["jpg", "png", "gif", "bitmap", "jpeg"])])
  submit = SubmitField("Post the Review")

  def validate_title(self, title):
    review = Review.query.filter_by(title=title.data).first()
    if review:
      raise ValidationError(
          "That game was already reviewed. Please check the review list or choose another game.")


class UpdateReviewForm(FlaskForm):
  title = StringField("Title of the Game",
                      validators=[DataRequired("You can't leave the review without a title."), Length(min=2)])
  platform = StringField("Platforms where the game's available",
                         validators=[DataRequired("In which platforms can you play it? You can't leave this section empty."), Length(min=3)])
  summary = TextAreaField("Short description about the game, it's genre and stuff like that",
                          validators=[DataRequired("Don't forget to add a short description, so they know what's going on."), Length(min=10)])
  content = TextAreaField("Actual content of the review", validators=[DataRequired(
      "A review without a review? You can't leave this section empty"), Length(min=20)])
  thumbnail = FileField("Upload a new thumbnail for the Review",
                        validators=[FileAllowed(["jpg", "png", "gif", "bitmap", "jpeg"])])
  submit = SubmitField("Save changes")


class PictureReviewForm(FlaskForm):
  pictures = FileField("Upload some pictures",
                       validators=[FileAllowed(["jpg", "png", "gif", "bitmap", "jpeg", "webp"], "Pictures Only!")])
  submit = SubmitField("Submit the pictures")
