from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, FileField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_wtf.file import FileAllowed, FileRequired

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class ForgetPasswordForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send OTP")

class VerifyPasswordForm(FlaskForm):
    otp = StringField("OTP", validators=[DataRequired(), Length(min=4, max=6)])
    submit = SubmitField("Verify OTP")

class ResetPasswordForm(FlaskForm):
    new_password = PasswordField("New Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField("Reset Password")

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField("Change Password")

class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    fullname = StringField("Full Name", validators=[Length(max=100)])
    bio = TextAreaField("Bio", validators=[Length(max=200)])
    submit = SubmitField("Update Profile")

class ChangePictureForm(FlaskForm):
    picture = FileField("Profile Picture", validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Only images are allowed!')
    ])
    submit = SubmitField("Upload Picture")

class RegisterVerifyForm(FlaskForm):
    otp = StringField("OTP", validators=[DataRequired(), Length(min=4, max=6)])
    submit = SubmitField("Verify")