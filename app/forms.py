from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app import db
import sqlalchemy as sa
from app.models import User
from flask_babel import lazy_gettext as _l


class LoginForm(FlaskForm):
    username = StringField(label=_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember me'), default=False)
    submit = SubmitField(_l('Login'))


class RegistrationForm(FlaskForm):
    username = StringField(label=_l('Username'), validators=[DataRequired()])
    email = EmailField(label=_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(label=_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(label=_l('Confirm password'), validators=[
                              DataRequired(), EqualTo('password')])
    about_me = StringField()

    submit = SubmitField(label=_l('Register'))

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError(_l('Please use different username'))

    def validate_email(self, email):
        user = db.session.scalar(
            sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError(_l('Please use a different email'))


class EditProfileForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    about_me = StringField(validators=[DataRequired()])
    submit = SubmitField()

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(
                User.username == username.data))
            if user:
                raise ValidationError(_l('Username already taken'))


class EmptyForm(FlaskForm):
    submit = SubmitField(_l('Submit'))


class PostForm(FlaskForm):
    post = TextAreaField(label=_l('Create new post'), validators=[
                         DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(label=_l('Submit'))


class ResetPasswordRequestForm(FlaskForm):
    email = EmailField(label=_l('Email address'), validators=[
                       Email(), DataRequired()])
    submit = SubmitField(label=_l('Request reset password'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(label=_l('Enter new password'),
                             validators=[DataRequired()])
    password2 = PasswordField(label=_l('Confirm new password'), validators=[
                              DataRequired(), EqualTo('password')])
    submit = SubmitField(label=_l('Reset Passeord'))
