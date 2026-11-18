from flask import Blueprint, flash, redirect, render_template, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.forms import LoginForm, RegistrationForm
from app.models import User


auth = Blueprint("auth", __name__)


@auth.route("/")
def index():
    return render_template("index.html")


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data.strip(), email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            if User.query.filter_by(email=user.email).first():
                flash("An account with that email already exists.", "error")
            else:
                raise
        else:
            session.clear()
            login_user(user)
            session.permanent = True
            return redirect(url_for("auth.dashboard"))

    return render_template("register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.is_active and user.check_password(form.password.data):
            session.clear()
            login_user(user)
            session.permanent = True
            return redirect(url_for("auth.dashboard"))

        flash("Email or password is incorrect.", "error")

    return render_template("login.html", form=form)


@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("auth.index"))


@auth.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")
