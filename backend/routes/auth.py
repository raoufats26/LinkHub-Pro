from flask import Blueprint, render_template, request, redirect, url_for, flash
from backend.models import User
from backend.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user
import re
import time

auth_bp = Blueprint("auth", __name__)

login_attempts = {}

def is_strong_password(password):
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"[0-9]", password)
    )

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("All fields are required.")
            return redirect(url_for("auth.register"))

        if not is_strong_password(password):
            flash("Password must be 8+ chars with uppercase, lowercase, and a number.")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("That email is already registered.")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(username=username).first():
            flash("That username is taken.")
            return redirect(url_for("auth.register"))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()

        flash("Account created! Please sign in.")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    ip = request.remote_addr

    if ip in login_attempts:
        attempts, last_time = login_attempts[ip]
        if attempts >= 5 and time.time() - last_time < 60:
            flash("Too many attempts. Try again in a minute.")
            return redirect(url_for("auth.login"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            login_attempts.pop(ip, None)
            return redirect(url_for("dashboard.index"))
        else:
            if ip not in login_attempts:
                login_attempts[ip] = [1, time.time()]
            else:
                login_attempts[ip][0] += 1
                login_attempts[ip][1] = time.time()
            flash("Invalid email or password.")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
