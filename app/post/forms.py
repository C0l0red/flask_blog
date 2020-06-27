from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length
from app.models import Comment

class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired("The post must have a title")])
    content = TextAreaField("Content", validators=[DataRequired("The post body must be filled"), Length(min=30, message="The body must be at least 30 characters long")])

class CommentForm(FlaskForm):
    comment = TextAreaField()
    id = TextAreaField(validators=[DataRequired()])
    
    def __init__(self, *args, user=None, post=None, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.post = post
        self.user = user

    def validate(self, *args, **kwargs):
        valid = super(CommentForm, self).validate(*args, **kwargs)

        if valid:
            exists = Comment.query.filter_by(user=self.user, post=self.post, comment=self.comment.data).first()

            if exists:
                self.comment.errors.append("Spam comments not allowed")
                
        return valid and not self.errors
    