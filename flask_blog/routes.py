import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flask_blog import app, bcrypt, db, mail
from flask_blog.forms import RegistrationForm, LoginForm, UpdateForm, PostForm, RequestResetForm, ResetPasswordForm
from flask_blog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    output = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output)

    if i.mode != 'RGB':
        i = i.convert("RGB")
    i.save(picture_path)

    return picture_fn

@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.dateposted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html', title='About Me')

@app.route('/contact')
def contact():
    return render_template('contacts.html', title='Contact Me')

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
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
        return redirect(url_for('login'))
    return render_template('register.html', title='register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login Succesful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='login', form=form)
    

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateForm()
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Account updated succesfully!!", 'info')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account', image_file=image_file , form=form)

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data, content = form.content.data, author = current_user)
        db.session.add(post)
        db.session.commit()
        flash("post uploaded succesfully", 'success')
        return(redirect(url_for('home')))
    return render_template('Create_Post.html', form=form, title=new_post, Legend="New Post")

@app.route('/post/<int:post_id>')
def post_page(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def post_update(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    if form.validate_on_submit():
        post.title = form.title.datas
        post.content = form.content.data
        db.session.commit()
        flash("Post Updated Successfully", "success")
        return redirect(url_for('post_page', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('Update.html', title="Update Post", post=post, form=form, Legend='Update Post')

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted Successfully", "success")
    return redirect(url_for('home'))

@app.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.dateposted.desc()).paginate(page=page, per_page=5)
    return render_template('user_post.html', posts=posts, user=user)


def send_email(user):
    token = user.get_reset_token()
    msg = Message("Password Reset Request", sender='noreply@gmail.com', recipients=[user.email])
    msg.body = f'''To reset your password click here:
{url_for('reset_password', token=token, _external=True)}
If you didnt request this please ignore and your account is safe'''
    mail.send(msg)


@app.route('/requestreset', methods=['GET', 'POST'])
def request_mail():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_email(user=user)
        flash("Instructions has been sent to the email", 'info')
        return redirect(url_for('home'))
    return render_template("request_reset.html", form=form, title="Forget Password")

@app.route('/resetpassword/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm()
    user = User.verify_token(token=token)
    if not user:
        flash('Token is invalid or expired', 'danger')
        return redirect(url_for('request_mail'))
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.commit()
        flash("Password changes Succesfully, You can now Log in", 'success')
        return redirect(url_for('login'))
    return render_template("ResetPassword.html", form=form, title='Reset Password')