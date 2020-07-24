from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired,Email,EqualTo
from wtforms import ValidationError
from flask_login import current_user
from Project.models import User

class LoginForm(FlaskForm):
    email = StringField('E-mail',[DataRequired('Email is required'),Email()])
    password = PasswordField('Password',[DataRequired('Password is required')])
    submit = SubmitField('Log In')

class RegisterForm(FlaskForm):
    email = StringField("E-mail",[DataRequired(),Email()])
    name = StringField("First Name",[DataRequired()])
    surname = StringField("Last Name",[DataRequired()])
    password = PasswordField("Password",[DataRequired(),EqualTo('confirm_password')])
    confirm_password = PasswordField("Confirm Password",[DataRequired()])
    submit = SubmitField("Register")

    def check_mail(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Email already registered with us.")

class ResetRequestForm(FlaskForm):
    email = StringField("E-mail",[DataRequired(),Email()])
    submit = SubmitField("Reset Password")

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("Email not registered.")

class PasswordResetForm(FlaskForm):
    password = PasswordField("Enter new Password",[DataRequired(),EqualTo('confirm_password')])
    confirm_password = PasswordField("Confirm new Password",[DataRequired()])
    submit = SubmitField("Continue")


