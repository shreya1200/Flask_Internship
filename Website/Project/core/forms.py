from Project.models import Feedback
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField
from wtforms.validators import DataRequired,Email

class FeedbackForm(FlaskForm):
    name = StringField('Name',[DataRequired()])
    email = StringField('E-mail',[DataRequired(),Email()])
    comment = TextAreaField('Comment',[DataRequired()])
    submit = SubmitField('Submit')
