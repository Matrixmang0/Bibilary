import re
import csv
from io import BytesIO
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, session, send_file
from email_validator import validate_email
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from models import (
    User,
    Librarian,
    Genre,
    Book,
    Request,
    Borrow,
    Purchase,
    Cart,
    Transaction,
    db,
)
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

    if not name or not description:
        flash("Please fill all the required fields")
        return redirect(url_for("add_genre"))

    if Genre.query.filter_by(name=name).first():
        flash("Genre already exists")
        return redirect(url_for("add_genre"))

    new_genre = Genre(name=name, date_created=datetime.now(), description=description)
    db.session.add(new_genre)
    db.session.commit()

    flash("Genre added successfully")
    return redirect(url_for("librarian"))


@app.route("/genre/<int:id>/")
@librarian_required
def show_genre(id):
    genre = Genre.query.get(id)
    if not genre:
        flash("Genre not found")
        return redirect(url_for("librarian"))
    return render_template("genre/show.html", genre=genre)


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


@app.route("/<int:genre_id>/book/add")
@librarian_required
def add_book(genre_id):
    genres = Genre.query.all()
    genre = Genre.query.get(genre_id)
    if not genre:
        flash("Genre not found")
        return redirect(url_for("librarian"))
    return render_template("book/add.html", genre=genre, genres=genres)


@app.route("/<int:genre_id>/book/add", methods=["POST"])
@librarian_required
def add_book_post(genre_id):
    title = request.form.get("title")
    authors = request.form.get("authors")
    genre_id_f = request.form.get("genre_id")
    quantity = request.form.get("quantity")
    price = request.form.get("price")
    summary = request.form.get("summary")
    image = request.files["image"]
    content = request.files["content"]

    if (
        not title
        or not authors
        or not genre_id_f
        or not quantity
        or not price
        or not summary
        or not image
        or not content
    ):
        flash("Please fill all the required fields")
        return redirect(url_for("add_book", genre_id=genre_id))

    if Book.query.filter_by(title=title).first():
        flash("Book already exists")
        return redirect(url_for("add_book", genre_id=genre_id))

    try:
        quantity = int(quantity)
    except ValueError:
        flash("Invalid quantity")
        return redirect(url_for("add_book", genre_id=genre_id))

    try:
        price = float(price)
    except ValueError:
        flash("Invalid price")
        return redirect(url_for("add_book", genre_id=genre_id))

    if int(quantity) <= 0:
        flash("Quantity should be a positive integer")
        return redirect(url_for("add_book", genre_id=genre_id))

    if float(price) < 0:
        flash("Price should be a positive float")
        return redirect(url_for("add_book", genre_id=genre_id))

    book = Book(
        title=title,
        authors=authors,
        genre_id=genre_id_f,
        quantity=quantity,
        price=price,
        summary=summary,
        image=image.read(),
        content=content.read(),
    )

    db.session.add(book)
    db.session.commit()

    flash("Book added successfully")
    return redirect(url_for("show_genre", id=genre_id_f))


@app.route("/<int:genre_id>/book/<int:book_id>/edit")
@librarian_required
def edit_book(genre_id, book_id):
    genres = Genre.query.all()
    genre = Genre.query.get(genre_id)
    book = Book.query.get(book_id)
    if not genre or not book:
        flash("Genre or book not found")
        return redirect(url_for("librarian"))
    return render_template("book/edit.html", genre=genre, genres=genres, book=book)


@app.route("/<int:genre_id>/book/<int:book_id>/edit", methods=["POST"])
@librarian_required
def edit_book_post(genre_id, book_id):

    title = request.form.get("title")
    authors = request.form.get("authors")
    genre_id_f = request.form.get("genre_id")
    quantity = request.form.get("quantity")
    price = request.form.get("price")
    summary = request.form.get("summary")
    image = request.files["image"]
    content = request.files["content"]

    if (
        not title
        or not authors
        or not genre_id_f
        or not quantity
        or not price
        or not summary
    ):
        flash("Please fill all the required fields")
        return redirect(url_for("edit_book", genre_id=genre_id, book_id=book_id))

    genre = Genre.query.get(genre_id_f)
    if not genre:
        flash("Genre not found")
        return redirect(url_for("edit_book", genre_id=genre_id, book_id=book_id))

    book = Book.query.get(book_id)
    if not book:
        flash("Book not found")
        return redirect(url_for("edit_book", genre_id=genre_id, book_id=book_id))

    if Book.query.filter_by(title=title).first() and title != book.title:
        flash("Book already exists")
        return redirect(url_for("edit_book", genre_id=genre_id, book_id=book_id))

    book.title = title
    book.authors = authors
    book.genre_id = genre_id_f
    book.quantity = quantity
    book.price = price
    book.summary = summary
    book.image = image.read() if image else book.image
    book.content = content.read() if content else book.content

    db.session.commit()
    flash("Book updated successfully")
    return redirect(url_for("show_genre", id=genre_id_f))


@app.route("/<int:genre_id>/genre/<int:book_id>/delete", methods=["POST", "GET"])
@librarian_required
def delete_book(book_id, genre_id):
    book = Book.query.get(book_id)
    if not book:
        flash("Book not found")
        return redirect(url_for("show_genre", id=genre_id))
    db.session.delete(book)
    db.session.commit()
    flash("book deleted successfully")
    return redirect(url_for("show_genre", id=genre_id))


@app.route("/user_requests")
@librarian_required
def user_requests():
    users = User.query.all()
    requests = Request.query.all()
    books = Book.query.all()
    genres = Genre.query.all()
    return render_template(
        "requests.html", requests=requests, users=users, books=books, genres=genres
    )


@app.route(
    "/user/<int:user_id>/accept_request/<int:request_id>", methods=["POST", "GET"]
)
@librarian_required
def accept_request(user_id, request_id):
    request = Request.query.get(request_id)
    user = User.query.get(user_id)
    book = Book.query.get(request.book_id)
    if not request:
        flash("Request not found")
        return redirect(url_for("user_requests"))
    if not user:
        flash("User not found")
        return redirect(url_for("user_requests"))
    days_requested = request.days_requested
    date_issued = datetime.now()
    date_due = date_issued + timedelta(days=days_requested)
    borrow = Borrow(
        user_id=user_id,
        book_id=request.book_id,
        date_issued=date_issued,
        date_due=date_due,
    )
    book.quantity -= 1
    db.session.add(borrow)
    db.session.delete(request)
    db.session.commit()
    flash("Request accepted successfully")
    return redirect(url_for("user_requests"))


@app.route("/request/<int:request_id>/reject", methods=["POST", "GET"])
@librarian_required
def reject_request(request_id):
    requested = Request.query.get(request_id)
    if not requested:
        flash("Request not found")
        return redirect(url_for("my_requests", user_id=session["user_id"]))
    db.session.delete(requested)
    db.session.commit()
    flash("Request rejected successfully")
    return redirect(url_for("user_requests"))


@app.route("/borrowed_books")
@librarian_required
def user_borrows():
    borrows = Borrow.query.all()
    users = User.query.all()
    books = Book.query.all()
    genres = Genre.query.all()
    today = datetime.now()

    for borrow in borrows:
        if borrow.date_due < today:
            db.session.delete(borrow)
            book = Book.query.get(borrow.book_id)
            book.quantity += 1
            db.session.commit()

    return render_template(
        "borrows.html",
        borrows=borrows,
        users=users,
        books=books,
        genres=genres,
        today=today,
    )


@app.route("/borrow/<int:borrow_id>/revoke", methods=["POST", "GET"])
@librarian_required
def revoke_borrow(borrow_id):
    borrow = Borrow.query.get(borrow_id)
    if not borrow:
        flash("Borrow not found")
        return redirect(url_for("user_borrows"))
    book = Book.query.get(borrow.book_id)
    book.quantity += 1
    db.session.delete(borrow)
    db.session.commit()
    return redirect(url_for("user_borrows"))


@app.route("/user_stats")
@librarian_required
def user_stats():
    genres = Genre.query.all()
    genre_names1 = [genre.name for genre in genres]
    genre_counts1 = [len(genre.books) for genre in genres]

    purchases = Purchase.query.all()
    genre2 = {}
    for purchase in purchases:
        if purchase.book.genre.name in genre2:
            genre2[purchase.book.genre.name] += 1
        else:
            genre2[purchase.book.genre.name] = 1
    genre_names2 = list(genre2.keys())
    genre_counts2 = list(genre2.values())

    borrows = Borrow.query.all()
    genre3 = {}
    for borrow in borrows:
        if borrow.book.genre.name in genre3:
            genre3[borrow.book.genre.name] += 1
        else:
            genre3[borrow.book.genre.name] = 1
    genre_names3 = list(genre3.keys())
    genre_counts3 = list(genre3.values())

    return render_template(
        "user_stats.html",
        genre_names1=genre_names1,
        genre_counts1=genre_counts1,
        genre_names2=genre_names2,
        genre_counts2=genre_counts2,
        genre_names3=genre_names3,
        genre_counts3=genre_counts3,
    )


# --------------- User routes --------------


@app.route("/")
def index():
    if session.get("user_id") == 10000:
        return redirect(url_for("librarian"))
    genres = Genre.query.all()
    books = Book.query.all()

    parameter = request.args.get("parameter")
    query = request.args.get("query")

    param_dict = {"genre": "Genre Name", "book": "Book Title", "price": "Max Price"}

    if parameter == "genre":
        genres = Genre.query.filter(Genre.name.ilike(f"%{query}%")).all()
    elif parameter == "book":
        return render_template(
            "index.html",
            genres=genres,
            books=books,
            parameter=parameter,
            query=query,
            param_dict=param_dict,
            show_search=True,
        )
    elif parameter == "price":
        return render_template(
            "index.html",
            genres=genres,
            books=books,
            parameter=parameter,
            query=float(query),
            param_dict=param_dict,
            show_search=True,
        )

    return render_template(
        "index.html",
        genres=genres,
        books=books,
        param_dict=param_dict,
        parameter=parameter,
        query=query,
        show_search=True,
    )


@app.route("/add_to_cart/<int:book_id>", methods=["POST", "GET"])
@auth_required
def add_to_cart(book_id):
    book = Book.query.get(book_id)
    if not book:
        flash("Book not found")
        return redirect(url_for("index"))
    cart = Cart.query.filter_by(user_id=session["user_id"], book_id=book_id).first()
    if cart:
        if cart.quantity < book.quantity:
            cart.quantity += 1
        else:
            flash("Book out of stock")
    else:
        cart = Cart(user_id=session["user_id"], book_id=book_id, quantity=1)
    db.session.add(cart)
    db.session.commit()

    flash("Book added to cart successfully")
    return redirect(url_for("cart"))


@app.route("/cart")
@auth_required
def cart():
    cart = Cart.query.filter_by(user_id=session["user_id"]).all()
    total = sum([item.book.price * item.quantity for item in cart])
    return render_template("cart.html", cart=cart, total=total)


@app.route("/cart/<int:cart_id>/delete", methods=["POST", "GET"])
@auth_required
def delete_cart(cart_id):
    cart = Cart.query.get(cart_id)
    if not cart:
        flash("Item not found")
        return redirect(url_for("cart"))
    if cart.user_id != session["user_id"]:
        flash("You are not authorized to delete this item")
        return redirect(url_for("cart"))
    db.session.delete(cart)
    db.session.commit()
    flash("Item deleted successfully")
    return redirect(url_for("cart"))


@app.route("/checkout", methods=["POST", "GET"])
@auth_required
def checkout():
    cart = Cart.query.filter_by(user_id=session["user_id"]).all()
    if not cart:
        flash("Cart is empty")
        return redirect(url_for("cart"))
    transaction = Transaction(user_id=session["user_id"], date_paid=datetime.now())
    db.session.add(transaction)
    for item in cart:
        purchase = Purchase(user_id=session["user_id"], date_purchased=datetime.now())
        quantity = int(request.form.get(f"quantity_{item.id}"))
        item_already_purchased = Purchase.query.filter_by(
            user_id=session["user_id"], book_id=item.book_id
        ).first()
        if item_already_purchased and item.book.quantity >= item.quantity:
            item_already_purchased.quantity += quantity
            item.book.quantity -= quantity
            db.session.add(item_already_purchased)
            db.session.delete(item)
        elif (
            item_already_purchased
            and item.book.quantity < item.quantity
            and item.book.quantity > 0
        ):
            flash(
                f"Reduced quantity of book {item.book.title} to {item.book.quantity} from {quantity} in cart"
            )
            return redirect(url_for("cart"))
        elif (
            item_already_purchased
            and item.book.quantity < item.quantity
            and item.book.quantity == 0
        ):
            flash("Book out of stock")
            return redirect(url_for("cart"))
        else:
            purchase.book_id = item.book_id
            purchase.quantity = quantity
            if item.book.quantity < item.quantity:
                flash("Book out of stock")
                return redirect(url_for("cart"))
            item.book.quantity -= quantity
            purchase.transaction_id = transaction.id
            db.session.add(purchase)
            db.session.delete(item)
    db.session.commit()
    flash("Purchase successful")
    return redirect(url_for("my_books"))


@app.route("/my_books")
@auth_required
def my_books():

    book_ids = (
        Purchase.query.filter_by(user_id=session["user_id"])
        .with_entities(Purchase.book_id)
        .all()
    )
    book_ids = [book_id for (book_id,) in book_ids]

    books = Book.query.filter(Book.id.in_(book_ids)).all()
    genres = Genre.query.filter(Genre.books.any(Book.id.in_(book_ids))).all()

    parameter = request.args.get("parameter")
    query = request.args.get("query")

    param_dict = {"genre": "Genre Name", "book": "Book Title"}

    if parameter == "genre":
        genres = Genre.query.filter(
            Genre.books.any(Book.id.in_(book_ids)), Genre.name.ilike(f"%{query}%")
        ).all()
    elif parameter == "book":
        return render_template(
            "my-books.html",
            genres=genres,
            books=books,
            parameter=parameter,
            query=query,
            param_dict=param_dict,
            show_search=True,
        )

    return render_template(
        "my-books.html",
        genres=genres,
        books=books,
        param_dict=param_dict,
        parameter=parameter,
        query=query,
        show_search=True,
    )


@app.route("/orders")
@auth_required
def orders():
    transactions = (
        Transaction.query.filter_by(user_id=session["user_id"])
        .order_by(Transaction.date_paid.desc())
        .all()
    )
    return render_template("orders.html", transactions=transactions)


@app.route("/export_csv")
@auth_required
def export_csv():
    transactions = Transaction.query.filter_by(user_id=session["user_id"]).all()
    url = "static/csv/transactions.csv"
    with open(url, "w") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["Transaction ID", "Date Paid", "Book Name", "Quantity", "Total Price"]
        )
        for transaction in transactions:
            for purchase in transaction.purchase:
                writer.writerow(
                    [
                        transaction.id,
                        transaction.date_paid,
                        purchase.book.title,
                        purchase.quantity,
                        purchase.book.price * purchase.quantity,
                    ]
                )
        return redirect(url)


@app.route("/<int:user_id>/my_stats")
@auth_required
def my_stats(user_id):
    purchases = Purchase.query.filter_by(user_id=user_id).all()
    book_ids = [purchase.book_id for purchase in purchases]
    genres = Genre.query.filter(Genre.books.any(Book.id.in_(book_ids))).all()
    genre_names1 = [genre.name for genre in genres]
    genre_counts1 = []
    for genre in genres:
        count = 0
        for purchase in purchases:
            if purchase.book.genre_id == genre.id:
                count += 1
        genre_counts1.append(count)

    borrows = Borrow.query.filter_by(user_id=user_id).all()
    book_ids = [borrow.book_id for borrow in borrows]
    genres = Genre.query.filter(Genre.books.any(Book.id.in_(book_ids))).all()
    genre_names2 = [genre.name for genre in genres]
    genre_counts2 = []
    for genre in genres:
        count = 0
        for borrow in borrows:
            if borrow.book.genre_id == genre.id:
                count += 1
        genre_counts2.append(count)

    return render_template(
        "my_stats.html",
        genre_names1=genre_names1,
        genre_counts1=genre_counts1,
        genre_names2=genre_names2,
        genre_counts2=genre_counts2,
    )


@app.route("/<int:user_id>/requests")
@auth_required
def my_requests(user_id):
    requests = Request.query.filter_by(user_id=user_id).all()
    books = Book.query.all()
    genres = Genre.query.all()
    return render_template(
        "user-requests.html", requests=requests, books=books, genres=genres
    )


@app.route("/add_to_request/<int:book_id>", methods=["POST"])
@auth_required
def add_to_request(book_id):
    book = Book.query.get(book_id)
    if not book:
        flash("Book not found")
    date_requested = datetime.now()
    days_requested = request.form.get("days_requested")
    requested = Request(
        user_id=session["user_id"],
        book_id=book.id,
        date_requested=date_requested,
        days_requested=days_requested,
    )
    db.session.add(requested)
    db.session.commit()
    return redirect(url_for("my_requests", user_id=session["user_id"]))


@app.route("/request/<int:request_id>/revoke", methods=["POST", "GET"])
@auth_required
def revoke_request(request_id):
    requested = Request.query.get(request_id)
    if not requested:
        flash("Request not found")
        return redirect(url_for("my_requests", user_id=session["user_id"]))
    db.session.delete(requested)
    db.session.commit()
    flash("Request revoked successfully")
    return redirect(url_for("my_requests", user_id=session["user_id"]))


@app.route("/my_borrows")
@auth_required
def my_borrows():
    borrows = Borrow.query.filter_by(user_id=session["user_id"]).all()
    books = Book.query.all()
    today = datetime.now()

    for borrow in borrows:
        if borrow.date_due < today:
            db.session.delete(borrow)
            book = Book.query.get(borrow.book_id)
            book.quantity += 1
            db.session.commit()
            return redirect(url_for("my_borrows"))

    book_ids = (
        Borrow.query.filter_by(user_id=session["user_id"])
        .with_entities(Borrow.book_id)
        .all()
    )
    book_ids = [book_id for (book_id,) in book_ids]

    books = Book.query.filter(Book.id.in_(book_ids)).all()
    genres = Genre.query.filter(Genre.books.any(Book.id.in_(book_ids))).all()

    parameter = request.args.get("parameter")
    query = request.args.get("query")

    param_dict = {"genre": "Genre Name", "book": "Book Title"}

    if parameter == "genre":
        genres = Genre.query.filter(
            Genre.books.any(Book.id.in_(book_ids)), Genre.name.ilike(f"%{query}%")
        ).all()
    elif parameter == "book":
        return render_template(
            "user-borrows.html",
            genres=genres,
            books=books,
            borrows=borrows,
            parameter=parameter,
            query=query,
            param_dict=param_dict,
            today=today,
            show_search=True,
        )

    return render_template(
        "user-borrows.html",
        genres=genres,
        books=books,
        borrows=borrows,
        param_dict=param_dict,
        parameter=parameter,
        query=query,
        today=today,
        show_search=True,
    )


@app.route("/borrow/<int:borrow_id>/return", methods=["POST", "GET"])
@auth_required
def return_borrow(borrow_id):
    borrow = Borrow.query.get(borrow_id)
    if not borrow:
        flash("Borrow not found")
    book = Book.query.get(borrow.book_id)
    book.quantity += 1
    db.session.delete(borrow)
    db.session.commit()
    flash(f"Book {book.title} returned successfully")
    return redirect(url_for("my_borrows"))
