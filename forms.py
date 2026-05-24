from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, EmailField
from wtforms.validators import DataRequired, Email, Length


class ContactForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=120)])
    email = EmailField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    subject = StringField("Subject", validators=[DataRequired(), Length(min=3, max=180)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(min=10, max=4000)])
