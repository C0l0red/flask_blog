from flask import current_app as app, redirect, render_template, flash, url_for, Blueprint, abort, request, flash
from app import db, login_manager
from .forms import CommentForm, PostForm
from flask_login import login_required, current_user
from app.models import BlogPost, User, Comment, UserSchema, CommentSchema, BlogPostSchema
from app.utils import ago as long_ago, dir_last_updated
from datetime import datetime
import bleach

post = Blueprint("post", __name__)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)
blogpost_schema = BlogPostSchema()
blogposts_schema = BlogPostSchema(many=True)

TAGS = ['h2', 'h3', 'h4', 'h5', 'h6', 'del', 'sub', 'sup', 'cite', 'strike', 'hr', 'samp', 's', 'code', 'pre', 
        'ins', 'img', 'canvas','u','br', 'font',
         'dt', 'dd', 'table', 'caption','th', 'tr', 'td', 'cole', 'thead', 'tbody', 'tfoot', 'style', 'span','p']

ATTRS = {
    "*": ['class', 'style', 'color', 'target']
}
STYLES = ["color", 'text-align', 'font-weight', 'margin-left', 'font-family']

@post.context_processor
def add_variables():
    return dict(comment_form=CommentForm,
                Comment=Comment)

@post.app_template_filter("ago")
def ago(date):
    return long_ago(date)

@post.route('/user/<username>')
@post.route('/user/<username>/<post_id>')
def home(username, post_id=None):
    user = User.query.filter_by(username=username).first_or_404()
    disabled = ""
    posts = user.posts.filter_by(is_published=True).order_by(BlogPost.date_posted.desc()).all()
    if current_user == user:
        posts = user.posts.order_by(BlogPost.date_posted.desc()).all()
    
    if post_id:
        posts = user.posts.filter_by(public_id=post_id, is_published=True).all()
        disabled = "disabled"
    
    return render_template('home.html', user=user, posts=posts,
                            last_updated=dir_last_updated('app/static'),
                            home_active='active', home_sr=' <span class="sr-only">(current)</span>',
                            disabled=disabled)

@post.route("/")
@post.route('/posts')
def posts():
    all_posts = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.date_posted.desc()).all()
    return render_template('posts.html', posts=all_posts, 
                            last_updated=dir_last_updated('app/static'),
                            posts_active ="active", posts_sr='<span class="sr-only">(current)</span>')

@post.route("/posts/<public_id>")
def single_post(public_id):
    post = BlogPost.query.filter_by(public_id=public_id).first_or_404()

    return render_template("post.html", post=post, last_updated=dir_last_updated('app/static'))



@post.route("/editor", methods=["GET", "POST"])
@post.route("/editor/<public_id>", methods=["GET", "POST"])
@login_required
def editor(public_id=None):
    #cleaned_data = 
    form = PostForm()
    if public_id:
        post = BlogPost.query.filter_by(public_id=public_id).first_or_404()
        if post.author != current_user:
            abort(403)
        form = PostForm(obj=post)

        if form.validate_on_submit():
            form.content.data = bleach.clean(form.content.data, tags=bleach.sanitizer.ALLOWED_TAGS + TAGS, 
                                            attributes={**bleach.sanitizer.ALLOWED_ATTRIBUTES, **ATTRS}, styles= bleach.sanitizer.ALLOWED_STYLES + STYLES)
            form.populate_obj(post)
            db.session.commit()
            return redirect(url_for('post.preview', public_id=post.public_id))


    if form.validate_on_submit():
 
        new_post = BlogPost(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('post.preview', public_id=new_post.public_id))
    
    if form.is_submitted():
        print(form.errors)
        for error in form.content.errors:
            flash(error, "danger")
        for error in form.title.errors:
            flash(error, "danger")

    return render_template("editor.html", form=form, 
                            last_updated =dir_last_updated('app/static'),
                            profile_active="active", profile_sr='<span class="sr-only">(current)</span>')


@post.route("/preview/<public_id>", methods=["GET", "POST"])
@login_required
def preview(public_id):
    post = BlogPost.query.filter_by(public_id=public_id).first_or_404()
    if current_user != post.author:
        abort(403)
    
    if request.method == "POST":
        if request.form.get("publish"):
            if not post.is_published:
                post.is_published = True
                post.date_published = datetime.utcnow()
        else:
            post.published = False
        db.session.commit()
        print(post.is_published)
        return redirect(url_for('post.home', username=current_user.username))

    return render_template("preview.html", post=post, 
                            last_updated=dir_last_updated('app/static'),
                            profile_active='active', profile_sr='<span class="sr-only">(current)</span>')
    


@post.route("/comment", methods=['POST'])
@login_required
def comment():
    if request.args.get("edit"):
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

