from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, InputRequired, EqualTo, Email, ValidationError
from app.models import User


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[Length(min=5, max=30), DataRequired()])
    email = StringField("Email", validators=[Email()])
    password = PasswordField("Password", validators=[Length(min=8), InputRequired()])
    password_confirm = PasswordField("Confirm Password", validators=[Length(min=8), EqualTo("password", message="Passwords must match")])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username already taken.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email already taken.")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

    def validate(self, *args, **kwargs):
        valid = super(LoginForm, self).validate(*args, **kwargs)
        
        if valid:
            user = User.query.filter_by(username=self.username.data).first()
            if user:
                check = user.check_password(self.password.data)
                if not check:
                    self.password.errors.append("Invalid login details")
            else:
                self.password.errors.append("Invalid login details")
                
        return valid and not self.password.errors


class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[Email()])

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError("Email not registered with any account.")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[Length(min=8), InputRequired()])
    password_confirm = PasswordField("Confirm Password", validators=[Length(min=8), EqualTo("password", message="Passwords must match")])

    def validate(self, *args, **kwargs):
        valid = super(ResetPasswordForm, self).validate(*args, **kwargs)
        
        if self.user.check_password(self.password.data):
            self.password.errors.append("You must set a new password")
        return valid and not self.errors


class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=20)])
    current_password = PasswordField("Current Password")
    email = StringField("Email",[Email(), DataRequired()])
    new_password = PasswordField("New Password")

    def validate_current_password(self, current_password):
        if current_password.data:
            if not self.user.check_password(current_password.data):
                raise ValidationError("Incorrect password")


    def validate(self, *args, **kwargs):
        valid = super(EditProfileForm, self).validate(*args, **kwargs)

        if self.current_password.data:
            if not self.current_password.errors:
                email_taken = User.query.filter_by(email=self.email.data).filter(-User.username==self.user.username).first()
                if email_taken:
                    self.email.errors.append("Email already registered to another account")
                same_password = self.user.check_password(self.new_password.data)
                if same_password:
                    self.new_password.errors.append("New password must be different")
        else:
            if self.email.data != self.user.email:
                self.email.errors.append("You need to enter your current password to change this")
            if self.new_password.data:
                self.new_password.errors("You need to enter your current password to change this")

        return valid and not self.errors