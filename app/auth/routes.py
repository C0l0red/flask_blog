from flask import current_app as app, redirect, render_template, flash, url_for, Blueprint, abort, request
from app import db, login_manager
from .forms import RegistrationForm, LoginForm, ForgotPasswordForm, ResetPasswordForm, EditProfileForm
from flask_login import login_required, login_user, logout_user, current_user
from app.models import User, Login
from app.utils import dir_last_updated

auth = Blueprint("auth", __name__)

@auth.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data,
                        email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        if form.sign_in.data:
            login_user(new_user)
            return redirect(url_for('post.posts'))
        return redirect(url_for('auth.login'))
    return render_template("register.html", form=form, title="Sign Up", last_updated=dir_last_updated('app/static'))

@auth.route("/login", methods= ['GET', "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('post.posts'))
    form = LoginForm()
    if not request.environ.get('HTTP_X_FORWARDED_FOR'):
        ip = request.environ.get("REMOTE_ADDR")
    else:
        ip = request.environ.get('HTTP_X_FORWARDED_FOR')
    device = request.headers.get("User-agent")

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            new_login = Login(ip_address=ip, device=device, user=user)
            db.session.add(new_login)
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for("post.posts"))

    return render_template("login.html", form=form, last_updated=dir_last_updated('app/static'))

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('post.posts'))

@auth.route("/forgot-password")
def forgot_password(done=False):
    if current_user.is_authenticated:
        return redirect(url_for('posts'))
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        user.send_mail(reset)
        return redirect(url_for("forgot_password", done=True))

    return render_template("forgot-password.html", form=form, done=done, last_updated=dir_last_updated('app/static'))

@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("posts"))
    user = User.validate_token(token)
    if user is None:
        return render_template("reset-password.html")

    form = ResetPasswordForm()
    form.user = user
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        print("ran")
        return redirect(url_for("post.posts"))

    return render_template("reset-password.html", form=form, last_updated=dir_last_updated('app/static'))

@auth.route("/edit-profile", methods=['GET', 'POST'])
@login_required
def edit_profile():
    if current_user != user:
        abort(403)
    form = EditProfileForm(obj=current_user)
    form.user = current_user

    if form.validate_on_submit():
        current_user.set_password(form.new_password.data)
        current_user.email = form.email.data
        current_user.username = form.username.data
        db.session.commit()
        return redirect(url_for("post.home", username=current_user.username))

    return render_template("edit-profile.html", form=form, last_updated=dir_last_updated('app/static'))