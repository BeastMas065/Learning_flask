
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