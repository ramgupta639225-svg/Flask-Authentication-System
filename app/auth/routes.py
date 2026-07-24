from flask_mail import Message
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from app.extensions import db, mail
from app.models import User
from app.auth.forms import (RegisterForm, LoginForm, ForgetPasswordForm, VerifyPasswordForm,
                            ResetPasswordForm, ChangePasswordForm, EditProfileForm, ChangePictureForm, RegisterVerifyForm)
from flask_login import login_user, login_required, current_user, logout_user
import random, time, os
from werkzeug.utils import secure_filename

auth = Blueprint("auth", __name__)


@auth.route("/")
def index():
    return render_template("auth/index.html")


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        otp = str(random.randint(100000, 999999))
        session["otp"] = otp
        session["otp_time"] = time.time()
        session["username"] = form.username.data
        session["email"] = form.email.data
        session["password"] = form.password.data
        msg = Message(
            subject="Verify Email",
            sender="ramgupta639225@gmail.com",
            recipients=[form.email.data]
        )
        msg.body = f"Your OTP is {otp}"
        mail.send(msg)
        flash("OTP sent to your email", "success")
        return redirect(url_for("auth.register_verify"))
    return render_template("auth/register.html", form=form)


@auth.route("/register_verify", methods=["GET", "POST"])
def register_verify():
    form = RegisterVerifyForm()
    if form.validate_on_submit():
        otp_time = session.get("otp_time")
        if not otp_time:
            flash("Session expired. Please register again.", "warning")
            return redirect(url_for("auth.register"))
        if time.time() - otp_time > 100:
            flash("OTP expired. Please resend OTP.", "danger")
            session.pop("otp", None)
            session.pop("otp_time", None)
            return redirect(url_for("auth.register_verify"))
        if form.otp.data != session.get("otp"):
            flash("Incorrect OTP. Please try again.", "danger")
            return render_template("auth/register_verify.html", form=form)
        user = User(
            username=session["username"],
            email=session["email"]
        )
        user.set_password(session["password"])
        db.session.add(user)
        db.session.commit()
        session.pop("otp", None)
        session.pop("otp_time", None)
        session.pop("username", None)
        session.pop("email", None)
        session.pop("password", None)
        flash("Account created successfully! Please login.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register_verify.html", form=form)


@auth.route("/resend_register_otp")
def resend_register_otp():
    email = session.get("email")
    if not email:
        flash("Session expired. Please register again.", "warning")
        return redirect(url_for("auth.register"))
    otp = str(random.randint(100000, 999999))
    session["otp"] = otp
    msg = Message(
        subject="Verify Email",
        sender="ramgupta639225@gmail.com",
        recipients=[email]
    )
    msg.body = f"Your new OTP is {otp}"
    mail.send(msg)
    flash("New OTP sent to your email.", "success")
    return redirect(url_for("auth.register_verify"))


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            form.email.errors.append("Email not found")
        elif not user.check_password(form.password.data):
            form.password.errors.append("Incorrect Password")
        else:
            login_user(user)
            flash("Welcome back!", "success")
            return redirect(url_for("auth.profile"))
    return render_template("auth/login.html", form=form)


@auth.route("/forget", methods=["GET", "POST"])
def forget():
    form = ForgetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            form.email.errors.append("Email not found")
        else:
            otp = str(random.randint(100000, 999999))
            session["otp"] = otp
            session["email"] = user.email
            session["otp_time"] = time.time()
            msg = Message(subject="Password Reset", sender="ramgupta639225@gmail.com", recipients=[user.email])
            msg.body = f"Your OTP is {otp}"
            mail.send(msg)
            flash("OTP sent to your email", "success")
            return redirect(url_for("auth.verify"))
    return render_template("auth/forget.html", form=form)


@auth.route("/verify", methods=["GET", "POST"])
def verify():
    form = VerifyPasswordForm()
    if form.validate_on_submit():
        otp_time = session.get("otp_time")
        if not otp_time:
            flash("Session expired. Generate OTP again.", "warning")
            return redirect(url_for("auth.verify"))
        if time.time() - otp_time > 100:
            flash("OTP expired. Generate a new one.", "danger")
            session.pop("otp", None)
            session.pop("otp_time", None)
            return redirect(url_for("auth.verify"))
        if form.otp.data != session.get("otp"):
            flash("Incorrect OTP. Please try again.", "danger")
        else:
            flash("OTP verified. Set new password.", "success")
            return redirect(url_for("auth.new_password"))
    return render_template("auth/verify.html", form=form)


@auth.route("/resend_otp")
def resend_otp():
    email = session.get("email")
    if not email:
        flash("Session expired. Please start again.", "warning")
        return redirect(url_for("auth.forget"))
    otp = str(random.randint(100000, 999999))
    session["otp"] = otp
    session["otp_time"] = time.time()
    msg = Message("OTP Verification", sender="ramgupta639225@gmail.com", recipients=[email])
    msg.body = f"Your New OTP is {otp}"
    mail.send(msg)
    flash("New OTP sent to your email", "success")
    return redirect(url_for("auth.verify"))


@auth.route("/new_password", methods=["GET", "POST"])
def new_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=session.get("email")).first()
        if user:
            user.set_password(form.new_password.data)
            db.session.commit()
            flash("Password reset successful. Please login.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash("User not found. Please try again.", "danger")
            return redirect(url_for("auth.forget"))
    return render_template("auth/new_password.html", form=form)


@auth.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ChangePictureForm()
    if form.validate_on_submit():
        picture = form.picture.data
        if picture:
            filename = secure_filename(picture.filename)
            upload_path = os.path.join(current_app.root_path, "static", "uploads", filename)
            picture.save(upload_path)
            current_user.picture = filename
            db.session.commit()
            flash("Profile picture updated successfully.", "success")
            return redirect(url_for("auth.profile"))
    return render_template("auth/profile.html", form=form)


@auth.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            form.current_password.errors.append("Old Password is incorrect")
            return render_template("auth/change_password.html", form=form)
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash("Password changed successfully!", "success")
        return redirect(url_for("auth.profile"))
    return render_template("auth/change_password.html", form=form)


@auth.route("/join")
@login_required
def join():
    return render_template("auth/join.html")


@auth.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if request.method == "GET":
        form.username.data = current_user.username
        form.fullname.data = current_user.fullname
        form.bio.data = current_user.bio
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user and existing_user.id != current_user.id:
            form.username.errors.append("Username already exists")
            return render_template("auth/edit_profile.html", form=form)
        current_user.username = form.username.data
        current_user.fullname = form.fullname.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("auth.profile"))
    return render_template("auth/edit_profile.html", form=form)


@auth.route("/security")
@login_required
def security():
    return render_template("auth/security.html")


@auth.route("/logout")
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out.", "info")
    return render_template("auth/index.html")


@auth.route("/delete_account")
@login_required
def delete_account():
    user = User.query.get(current_user.id)
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash("Your account has been deleted.", "danger")
    return redirect(url_for("auth.login"))