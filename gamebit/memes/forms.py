from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class MemeForm(FlaskForm):
  meme = FileField("Upload a meme",
                   validators=[FileAllowed(["jpg", "png", "gif", "bitmap", "jpeg", "webp"], "Pictures Only!")])
  caption = StringField("Write a caption for your meme",
                        validators=[DataRequired("You can't leave the meme without a caption."), Length(min=2)])
  submit = SubmitField("Submit the pictures")
