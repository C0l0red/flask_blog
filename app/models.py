from . import db, login_manager, ma
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from flask_login import UserMixin
import jwt
from flask import current_app as app
from flask.cli import with_appcontext
from uuid import uuid4
from app.utils import ago
from sqlalchemy.ext.hybrid import hybrid_property

make_uuid = (lambda: uuid4().hex.upper()[0:15])

class ModelMixin:
    def save(self):
        db.session.add(self)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

likes = db.Table("likes", 
    db.Column("user_id", db.Integer,db.ForeignKey('user.id'), primary_key=True),
    db.Column("blog_post_id", db.Integer, db.ForeignKey("blog_post.id"), primary_key=True)
    )

dislikes = db.Table("dislikes", 
    db.Column("user_id", db.Integer,db.ForeignKey('user.id'), primary_key=True),
    db.Column("blog_post_id", db.Integer, db.ForeignKey("blog_post.id"), primary_key=True)
    )

class User(db.Model, UserMixin, ModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(15), default=make_uuid)
    username = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return self.username

    def set_password(self, password):
        hash_ = generate_password_hash(password, method="sha256")
        self.password = hash_

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def create_token(self):
        token = jwt.encode({"username":self.username, "exp": datetime.utcnow() + timedelta(minutes=30)}, app.config["SECRET_KEY"])
        return token.decode("UTF-8")

    @staticmethod
    def validate_token(token):
        try:
            data = jwt.decode(token, app.config["SECRET_KEY"])
            current_user = User.query.filter_by(username=data['username']).first()
        except:
            return None
        
        return current_user

class UserSchema(ma.Schema):
    class Meta:
        fields = ("public_id", "username", "email")

    _links = ma.Hyperlinks(
        {"self": ma.URLFor("post.home", username="<username>")}
    )

class BlogPost(db.Model, ModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(15), default=make_uuid)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_published = db.Column(db.DateTime)
    edited = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=False)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship("User", backref=db.backref('posts',lazy='dynamic'), lazy=True)
    likes = db.relationship("User", backref='liked_posts', secondary="likes", collection_class=set, lazy="dynamic")
    dislikes = db.relationship("User", backref='disliked_posts', secondary="dislikes", collection_class=set, lazy="dynamic")
    
    def __repr__(self):
        return 'Blog post ' + str(self.id)

    def dislike(self, user):
        if user in self.dislikes.all():
            self.dislikes.remove(user)
        else:
            if user in self.likes.all():
                self.likes.remove(user)
            self.dislikes.append(user)
        return user in self.dislikes.all()

    def like(self, user):
        if user in self.likes.all():
            self.likes.remove(user)
        else:
            if user in self.dislikes.all():
                self.dislikes.remove(user)
            self.likes.append(user)
        return user in self.likes.all()
    
    def in_(self, user):
        return user in self.likes.all(), user in self.dislikes.all()

class BlogPostSchema(ma.Schema):
    class Meta:
        fields = ("public_id", "title", "content", "likes", "dislikes", "user")

    user = ma.Nested(UserSchema)
    likes = ma.Nested(UserSchema, many=True)
    dislikes = ma.Nested(UserSchema, many=True)
    _links = ma.Hyperlinks(
        {"self": ma.URLFor("post.single_post", public_id="<public_id>"), "collection": ma.URLFor("post.posts")}
    )        

class Login(db.Model, ModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(20))
    device = db.Column(db.Text)
    time = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    user = db.relationship("User", backref='logins', lazy="joined")

class LoginSchema(ma.Schema):
    class Meta:
        fields = ("ip_address", "time", "device", "user")

    user = ma.Nested(UserSchema)

class Comment(db.Model, ModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(15), default=make_uuid)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("blog_post.id"))
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    parent = db.relationship('Comment', backref="sub_comments", remote_side=id)
    time_created = db.Column(db.DateTime, default=datetime.utcnow)
    edited = db.Column(db.Boolean, default=False)

    comment = db.Column(db.Text, nullable=False)
    user = db.relationship("User", backref="comments", lazy=True)
    post = db.relationship("BlogPost", backref=db.backref('comments', lazy="dynamic"))

    @hybrid_property
    def ago(self):
        return ago(self.time_created)

class CommentSchema(ma.Schema):
    class Meta:
        fields = ("public_id", "time_created", "comment", "user", "ago")

    user = ma.Nested(UserSchema)

