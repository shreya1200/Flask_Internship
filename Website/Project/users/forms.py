from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,IntegerField
from wtforms.validators import DataRequired,Email,EqualTo,Length
from wtforms import ValidationError
from flask_login import current_user
from Project.models import User

class LoginForm(FlaskForm):
    email = StringField('email',[DataRequired('Email is required')])
    password = PasswordField('password',[DataRequired('Password is required')])
    submit = SubmitField('Log In')

class RegisterForm(FlaskForm):
    name = StringField("First Name",[DataRequired()])
    email = StringField("E-mail",[DataRequired(),Email()])
    number = IntegerField("number",[DataRequired()])
    username = StringField("username",[DataRequired()])
    password = PasswordField("Password",[DataRequired(),Length(min=6, message='Select a stronger password.'),EqualTo('confirm_password', message='Passwords must match.')])
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


