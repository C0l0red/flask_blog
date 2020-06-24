from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, InputRequired, EqualTo, Email, ValidationError
from app.models import User

class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=20)])
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    email = StringField("Email",[Email(), DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired()])

    def validate_current_password(self, current_password):
        if not self.user.check_password(current_password.data):
            raise ValidationError("Incorrect password")

    def validate_new_password(self, new_password):
        if not self.validate_current_password():
            raise ValidationError("Current password is required to set this field")
            return
        if new_password == self.current_password.data:
            raise ValidationError("New password must be different")

    def validate_email(self, email):
        if not self.validate_current_password():
            raise ValidationError("Current password is required to set this field")
            return
        if self.user.email == email.data:
            raise ValidationError("New email must be different")
        elif User.query.filter_by(email=email.data).first():
            raise ValidationError("Email already registered to a different account")