from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import current_user, login_required, login_user, logout_user
from flask_blog import db, bcrypt
from flask_blog.models import User, Post
from flask_blog.users.forms import RegistrationForm, LoginForm, UpdateForm, RequestResetForm, ResetPasswordForm
from flask_blog.users.utils import save_picture, send_email

users = Blueprint("users", __name__)

@users.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8") 
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            user = User(username=form.username.data, email = form.email.data, password = hashed_password, image_file = picture_file)     
        else:
            user = User(username=form.username.data, email = form.email.data, password = hashed_password)    
        db.session.add(user)
        db.session.commit()
        flash("Acoount Created!!, You can now log in", 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='register', form=form)

@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login Succesful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='login', form=form)
    
@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateForm()
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        if form.default.data:
            current_user.image_file = 'default.jpg'
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Account updated succesfully!!", 'info')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account', image_file=image_file , form=form)

@users.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.dateposted.desc()).paginate(page=page, per_page=5)
    return render_template('user_post.html', posts=posts, user=user)

@users.route('/requestreset', methods=['GET', 'POST'])
def request_mail():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_email(user=user)
        flash("Instructions has been sent to the email", 'info')
        return redirect(url_for('main.home'))
    return render_template("request_reset.html", form=form, title="Forget Password")

@users.route('/resetpassword/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm()
    user = User.verify_token(token=token)
    if not user:
        flash('Token is invalid or expired', 'danger')
        return redirect(url_for('users.request_mail'))
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.commit()
        flash("Password changes Succesfully, You can now Log in", 'success')
        return redirect(url_for('users.login'))
    return render_template("ResetPassword.html", form=form, title='Reset Password')