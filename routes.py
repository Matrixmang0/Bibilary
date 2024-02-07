import re
from flask import render_template, request, redirect, url_for, flash
from email_validator import validate_email
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Librarian, Genre, Book, Request, Borrow, db
from app import app


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register_post():
    username = request.form.get("username")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    email = request.form.get("email")
    name = request.form.get("name")

    if not username or not password or not confirm_password or not email or not name:
        flash("Please fill all the fields")
        return redirect(url_for("register"))

    if password != confirm_password:
        flash("Passwords do not match")
        return redirect(url_for("register"))

    if not validate_email(email):
        flash("Please enter a valid email address")
        return redirect(url_for("register"))

    if len(password) < 8:
        flash("Password should be at least 8 characters long")
        return redirect(url_for("register"))

    if not re.search(r"[A-Z]", password):
        flash("Password should contain at least one uppercase letter")
        return redirect(url_for("register"))

    if not re.search(r"[a-z]", password):
        flash("Password should contain at least one lowercase letter")
        return redirect(url_for("register"))

    if not re.search(r"\d", password):
        flash("Password should contain at least one digit")
        return redirect(url_for("register"))

    user = User.query.filter_by(username=username).first()

    if user:
        flash("Username already exists")
        return redirect(url_for("register"))

    password_hash = generate_password_hash(password)

    new_user = User(username=username, passhash=password_hash, email=email, name=name)

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("login"))


@app.route("/login")
def login():
    return render_template("login.html")
