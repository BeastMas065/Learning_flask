from flask_wtf import FlaskForm 
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
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
    picture = FileField("Upload Profile Picture", validators=[FileAllowed(['jpg', 'png'])])
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
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField("Update")
    
    def validate_username(self, username):
        if current_user.username != username.data:
            name = User.query.filter_by(username=username.data).first()
            if name:
                raise ValidationError("Username Taken, try another one")

    def validate_email(self, email):
        if current_user.email != email.data:
            name = User.query.filter_by(email=email.data).first()
            if name:
                raise ValidationError("User with Email already exists, try loggin in")
            
class PostForm(FlaskForm):
    title = StringField('Title', validators = [DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Upload Post")


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")
    
    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if not user:
            raise ValidationError("User with this email does not exist, Create account")

class ResetPasswordForm(FlaskForm):
    password = StringField('New Password', validators=[DataRequired()])
    confirm_password = StringField('Confirm Password', validators=[DataRequired()]) 
    submit = SubmitField('Reset')