import re
from io import BytesIO
from datetime import date
from flask import render_template, request, redirect, url_for, flash, session, send_file
from email_validator import validate_email
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from models import User, Librarian, Genre, Book, Request, Borrow, db
from app import app

# --------------- Decorators ---------------


def librarian_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("You need to login or register to access this page")
            return redirect(url_for("login"))
        librarian = Librarian.query.get(session["user_id"])
        if not librarian:
            flash("You are not authorized to access this page")
            return redirect(url_for("index"))
        return func(*args, **kwargs)

    return wrapper


def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("You need to login or register to access this page")
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return wrapper


# ----------------- Routes -----------------


@app.route("/")
@auth_required
def index():
    user = User.query.get(session["user_id"])
    if not user:
        return redirect(url_for("librarian"))
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


@app.route("/login", methods=["POST"])
def login_post():
    username_email = request.form.get("username-email")
    password = request.form.get("password")

    if not username_email or not password:
        flash("Please fill all the fields")
        return redirect(url_for("login"))

    user = User.query.filter_by(username=username_email).first()
    if user is None:
        user = User.query.filter_by(email=username_email).first()
    librarian = Librarian.query.filter_by(username=username_email).first()
    if librarian is None:
        librarian = Librarian.query.filter_by(email=username_email).first()

    if user is None and librarian is None:
        flash("Username or email does not exist")
        return redirect(url_for("login"))

    if user:
        if not check_password_hash(user.passhash, password):
            flash("Incorrect password")
            return redirect(url_for("login"))
    else:
        if not check_password_hash(librarian.passhash, password):
            flash("Incorrect password")
            return redirect(url_for("login"))

    session["user_id"] = user.id if user else librarian.id
    return redirect(url_for("index"))


@app.route("/profile")
@auth_required
def profile():
    user = User.query.get(session["user_id"])
    librarian = Librarian.query.get(session["user_id"])
    return render_template("profile.html", user=user, librarian=librarian)


@app.route("/profile", methods=["POST"])
@auth_required
def profile_update():
    name = request.form.get("name")
    email = request.form.get("email")
    username = request.form.get("username")

    if not name or not email or not username:
        flash("Please fill all the fields")
        return redirect(url_for("profile"))

    user = User.query.get(session["user_id"])
    librarian = Librarian.query.get(session["user_id"])

    if user:
        if user.username != username:
            new_username = User.query.filter_by(username=username).first()
            if new_username:
                flash("Username already exists")
                return redirect(url_for("profile"))
        if user.email != email:
            new_email = User.query.filter_by(email=email).first()
            if new_email:
                flash("Email already exists")
                return redirect(url_for("profile"))
        user.name = name
        user.email = email
        user.username = username
    else:
        if librarian.username != username:
            new_username = Librarian.query.filter_by(username=username).first()
            if new_username:
                flash("Username already exists")
                return redirect(url_for("profile"))
        if librarian.email != email:
            new_email = Librarian.query.filter_by(email=email).first()
            if new_email:
                flash("Email already exists")
                return redirect(url_for("profile"))
        librarian.name = name
        librarian.email = email
        librarian.username = username

    db.session.commit()
    flash("Profile updated successfully")
    return redirect(url_for("profile"))


@app.route("/profile/change-password")
@auth_required
def change_password():
    return render_template("change-password.html")


@app.route("/profile/change-password", methods=["POST"])
@auth_required
def change_password_post():
    cpassword = request.form.get("cpassword")
    npassword = request.form.get("npassword")
    rnpassword = request.form.get("rnpassword")

    if not cpassword or not npassword or not rnpassword:
        flash("Please fill all the fields")
        return redirect(url_for("change_password"))

    user = User.query.get(session["user_id"])
    librarian = Librarian.query.get(session["user_id"])

    if npassword != rnpassword:
        flash("New passwords do not match")
        return redirect(url_for("change_password"))
    if len(npassword) < 8:
        flash("New password should be at least 8 characters long")
        return redirect(url_for("change_password"))
    if not re.search(r"[A-Z]", npassword):
        flash("New password should contain at least one uppercase letter")
        return redirect(url_for("change_password"))
    if not re.search(r"[a-z]", npassword):
        flash("New password should contain at least one lowercase letter")
        return redirect(url_for("change_password"))
    if not re.search(r"\d", npassword):
        flash("New password should contain at least one digit")
        return redirect(url_for("change_password"))

    if user:
        if not check_password_hash(user.passhash, cpassword):
            flash("Incorrect password")
            return redirect(url_for("change_password"))
        user.passhash = generate_password_hash(npassword)
    else:
        if not check_password_hash(librarian.passhash, cpassword):
            flash("Incorrect password")
            return redirect(url_for("change_password"))
        librarian.passhash = generate_password_hash(npassword)

    db.session.commit()
    flash("Password changed successfully")
    return redirect(url_for("profile"))


@app.route("/logout")
@auth_required
def logout():
    session.pop("user_id")
    return redirect(url_for("login"))


@app.route("/<int:genre_id>/image")
def get_genre_image(id):
    genre = Genre.query.get(id)
    if genre and genre.image:
        return send_file(BytesIO(genre.image), mimetype="image/png")
    else:
        return send_file("static/placeholder.png", mimetype="image/png")


@app.route("/librarian")
@librarian_required
def librarian():
    genres = Genre.query.all()
    return render_template("librarian.html", genres=genres)


@app.route("/genre/add")
@librarian_required
def add_genre():
    return render_template("genre/add.html")


@app.route("/genre/add", methods=["POST"])
@librarian_required
def add_genre_post():
    name = request.form.get("name")
    description = request.form.get("description")
    image = request.files["image"]

    if not name or not description:
        flash("Please fill all the required fields")
        return redirect(url_for("add_genre"))

    if Genre.query.filter_by(name=name).first():
        flash("Genre already exists")
        return redirect(url_for("add_genre"))

    new_genre = Genre(
        name=name,
        date_created=date.today(),
        description=description,
        image=image.read() if image else None,
    )
    db.session.add(new_genre)
    db.session.commit()

    flash("Genre added successfully")
    return redirect(url_for("librarian"))


@app.route("/genre/<int:id>/")
@librarian_required
def show_genre(id):
    return "Hello"


@app.route("/genre/<int:id>/edit")
@librarian_required
def edit_genre(id):
    genre = Genre.query.get(id)
    if not genre:
        flash("Genre not found")
        return redirect(url_for("librarian"))
    return render_template("genre/edit.html", genre=genre)


@app.route("/genre/<int:id>/edit", methods=["POST"])
@librarian_required
def edit_genre_post(id):
    name = request.form.get("name")
    description = request.form.get("description")
    image = request.files["image"]

    if not name or not description:
        flash("Please fill all the required fields")
        return redirect(url_for("edit_genre", id=id))

    genre = Genre.query.get(id)
    if not genre:
        flash("Genre not found")
        return redirect(url_for("librarian"))

    if Genre.query.filter_by(name=name).first() and name != genre.name:
        flash("Genre already exists")
        return redirect(url_for("edit_genre", id=id))

    genre.name = name
    genre.description = description
    genre.image = image.read() if image else genre.image

    db.session.commit()
    flash("Genre updated successfully")
    return redirect(url_for("librarian"))


@app.route("/genre/<int:id>/delete", methods=["POST", "GET"])
@librarian_required
def delete_genre(id):
    genre = Genre.query.get(id)
    if not genre:
        flash("Genre not found")
        return redirect(url_for("librarian"))
    db.session.delete(genre)
    db.session.commit()
    flash("Genre deleted successfully")
    return redirect(url_for("librarian"))
