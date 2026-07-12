from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import current_user, login_required
from flask_blog import db
from flask_blog.models import Post
from flask_blog.posts.forms import PostForm

posts = Blueprint("posts", __name__)

@posts.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data, content = form.content.data, author = current_user)
        db.session.add(post)
        db.session.commit()
        flash("post uploaded succesfully", 'success')
        return(redirect(url_for('main.home')))
    return render_template('Create_Post.html', form=form, title="new_post", Legend="New Post")

@posts.route('/post/<int:post_id>')
def post_page(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def post_update(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Post Updated Successfully", "success")
        return redirect(url_for('posts.post_page', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('Update.html', title="Update Post", post=post, form=form, Legend='Update Post')

@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted Successfully", "success")
    return redirect(url_for('main.home'))


