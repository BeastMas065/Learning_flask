from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_blog.models import User

class RegistrationForm(FlaskForm):
    username =StringField(
        'Username',
        validators = [DataRequired(), Length(min=2, max=20)])
    email = StringField(
        'Email',
        validators = [DataRequired(), Email()])
    password = PasswordField(
        'Password',
        validators = [DataRequired(),Length(min=3,max=15)])
    confirm_password = PasswordField(
        'Confirm Password',
        validators = [DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        name = User.query.filter_by(username=username.data).first()
        if name:
            raise ValidationError("Username Taken, try another one")

    def validate_email(self, email):
        name = User.query.filter_by(email=email.data).first()
        if name:
            raise ValidationError("User with wamail already exists, try loggin in")
    
class LoginForm(FlaskForm):
    email =StringField(
        'Email',
        validators = [DataRequired(),Email()])
    password = PasswordField(
        'Password',
        validators = [DataRequired(),Length(min=3,max=15)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateForm(FlaskForm):
    username =StringField(
        'Username',
        validators = [DataRequired(), Length(min=2, max=20)])
    email = StringField(
        'Email',
        validators = [DataRequired(), Email()])
    
    def validate_username(self, username):
        name = User.query.filter_by(username=username.data).first()
        if name:
            raise ValidationError("Username Taken, try another one")

    def validate_email(self, email):
        name = User.query.filter_by(email=email.data).first()
        if name:
            raise ValidationError("User with wamail already exists, try loggin in")