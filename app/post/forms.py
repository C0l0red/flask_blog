from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length
from app.models import Comment

class NewPostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired(), Length(min=30)])

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
    