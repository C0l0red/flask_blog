from flask import current_app as app, redirect, render_template, flash, url_for, Blueprint, abort, request
from app import db, login_manager
from .forms import CommentForm, NewPostForm
from flask_login import login_required, current_user
from app.models import BlogPost, User, Comment, UserSchema, CommentSchema, BlogPostSchema
from app.utils import ago as long_ago
from datetime import datetime

post = Blueprint("post", __name__)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)
blogpost_schema = BlogPostSchema()
blogposts_schema = BlogPostSchema(many=True)


@post.context_processor
def add_variables():
    return dict(comment_form=CommentForm,
                Comment=Comment)

@post.app_template_filter("ago")
def ago(date):
    return long_ago(date)

@post.route('/user/<int:id>', methods=["GET", "POST"])
def home(id):
    user = User.query.get_or_404(id)
    posts = BlogPost.query.filter_by(author=user).order_by(BlogPost.date_posted.desc())
    form = NewPostForm()
    if form.validate_on_submit():
        post = BlogPost.query.filter_by(title=form.title.data).first()
        if post:
            return redirect(url_for("post.home", id=user.id))
        new_post = BlogPost(title=form.title.data, content=form.content.data, author=user)
        db.session.add(new_post)
        db.session.commit()
        return {"title": new_post.title,
                "content": new_post.content,
                "id": new_post.id,
                "ago": ago(new_post.date_posted)}
    return render_template('home.html', form=form, user=user, posts=posts)

@post.route("/")
@post.route('/posts')
def posts():
    all_posts = BlogPost.query.order_by(BlogPost.date_posted.desc()).all()
    return render_template('posts.html', posts=all_posts)

@post.route("/posts/<public_id>")
def single_post(public_id):
    post = BlogPost.query.filter_by(public_id=public_id).first_or_404()

    return render_template("post.html", post=post)


@post.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = BlogPost.query.get_or_404(id)
    form = CreateForm(obj=post)

    if post.author != current_user:
        abort(403)
    #form.title.data = post.title
    #form.content.data = post.conten#t

    if form.validate_on_submit():
        if form.content.data == post.content and form.title.data == post.title:
            return redirect(url_for("posts"))
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        return redirect(url_for("post.home", id=post.author.id))
    
    return render_template('edit.html', post=post, form=form)


@post.route("/comment", methods=['GET', 'POST'])
@login_required
def comment():
    if "edit" in request.args:
        comment = Comment.query.filter_by(public_id = request.form["id"]).first_or_404()
        if comment.user != current_user:
            abort(403)
        comment.comment = request.form["comment"]
        comment.edited = True
        db.session.commit()
        return {"status":"success"}
    post = BlogPost.query.filter_by(public_id=request.form["id"]).first_or_404()
    form = CommentForm(post=post, user=current_user)
    if form.validate_on_submit():
        new_comment = Comment(comment=form.comment.data, 
                              user=current_user,
                              time_created=datetime.utcnow())
        post.comments.append(new_comment)
        db.session.commit()
        comment = comment_schema.dump(new_comment)
        print(comment)
        return comment
    
    else:
        return { "error": form.errors }


@post.route("/delete/<type_>/<public_id>", methods=['POST'])
@login_required
def delete(type_, public_id):
    if type_ == "comment":
        comment = Comment.query.filter_by(public_id=public_id).first_or_404()
        if comment.user != current_user:
            abort(403)
        entry = comment
    elif type_ == "post":
        post = BlogPost.query.filter_by(public_id=public_id).first_or_404()
        if post.author != current_user:
            abort(403)
        entry = post

    db.session.delete(entry)
    db.session.commit()
    return {"status": "success"}

@post.route("/react", methods=["POST"])
def react():
    if not current_user.is_authenticated:
        return {"redirect": "/login"}
    liked = disliked = False
    form = request.form
    post = BlogPost.query.filter_by(public_id=form["id"]).first()
    print("post found")
    if form['reaction'] == "Like":
        liked = post.like(current_user)
        print("like completed")
    elif form['reaction'] == "Dislike":
        disliked = post.dislike(current_user)
        print("dislike completed")
    
    db.session.commit()
    print("session committed")
    
    likes, dislikes = post.likes.count(), post.dislikes.count()

    return {"liked": liked,
            "disliked": disliked,
            "likes": f"{likes} {'Like' if likes == 1 else 'Likes'}",
            "dislikes": f"{dislikes} {'Dislike' if dislikes == 1 else 'Dislikes'}"}

@post.route("/index")
def index():

    return render_template('index.html')

