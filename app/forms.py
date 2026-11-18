import re

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import (
    DataRequired,
    EqualTo,
    InputRequired,
    Length,
    ValidationError,
)


def validate_email(form, field):
    email = field.data.strip()
    if len(email) > 254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ValidationError("Enter a valid email address.")


class RegistrationForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(max=100)],
    )
    email = StringField(
        "Email",
        filters=[lambda value: value.strip().lower()],
        validators=[InputRequired(), validate_email],
    )
    password = PasswordField(
        "Password",
        validators=[
            InputRequired(),
            Length(min=12, max=128, message="Use 12 to 128 characters."),
        ],
    )
    confirm_password = PasswordField(
        "Confirm password",
        validators=[
            InputRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Create account")


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        filters=[lambda value: value.strip().lower()],
        validators=[InputRequired(), validate_email],
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(max=128)],
    )
    submit = SubmitField("Sign in")
