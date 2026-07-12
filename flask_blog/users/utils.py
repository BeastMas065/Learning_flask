import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_blog import mail
from flask_mail import Message

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    
    output = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output)

    if i.mode != 'RGB':
        i = i.convert("RGB")
    i.save(picture_path)

    return picture_fn

def send_email(user):
    token = user.get_reset_token()
    msg = Message("Password Reset Request", sender='noreply@gmail.com', recipients=[user.email])
    msg.body = f'''To reset your password click here:
{url_for('users.reset_password', token=token, _external=True)}
If you didnt request this please ignore and your account is safe'''
    mail.send(msg)
