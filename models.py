from app import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(14), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    passhash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    feedbacks = db.relationship(
        "Feedback", cascade="all, delete-orphan", backref="user", lazy=True
    )
    requests = db.relationship(
        "Request", cascade="all, delete-orphan", backref="user", lazy=True
    )
    borrows = db.relationship(
        "Borrow", cascade="all, delete-orphan", backref="user", lazy=True
    )
    purchases = db.relationship(
        "Purchase", cascade="all, delete-orphan", backref="user", lazy=True
    )
    carts = db.relationship(
        "Cart", cascade="all, delete-orphan", backref="user", lazy=True
    )
    transaction = db.relationship(
        "Transaction", cascade="all, delete-orphan", backref="user", lazy=True
    )


class Librarian(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(14), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    passhash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(120), nullable=False)


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String, nullable=False)
    books = db.relationship(
        "Book", cascade="all, delete-orphan", backref="genre", lazy=True
    )


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    authors = db.Column(db.String(120), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    summary = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=True)
    content = db.Column(db.String, nullable=False)
    feedbacks = db.relationship(
        "Feedback", cascade="all, delete-orphan", backref="book", lazy=True
    )
    requests = db.relationship(
        "Request", cascade="all, delete-orphan", backref="book", lazy=True
    )
    borrows = db.relationship(
        "Borrow", cascade="all, delete-orphan", backref="book", lazy=True
    )
    purchases = db.relationship(
        "Purchase", cascade="all, delete-orphan", backref="book", lazy=True
    )
    carts = db.relationship(
        "Cart", cascade="all, delete-orphan", backref="book", lazy=True
    )


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    date_requested = db.Column(db.DateTime, nullable=False)
    days_requested = db.Column(db.Integer, nullable=False)


class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    date_issued = db.Column(db.DateTime, nullable=False)
    date_due = db.Column(db.DateTime, nullable=False)


class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    transaction_id = db.Column(
        db.Integer, db.ForeignKey("transaction.id"), nullable=False
    )
    date_purchased = db.Column(db.DateTime, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date_paid = db.Column(db.DateTime, nullable=False)
    purchase = db.relationship(
        "Purchase", cascade="all, delete-orphan", backref="transaction", lazy=True
    )


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    subject = db.Column(db.String, nullable=False)
    ratings = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String, nullable=False)


with app.app_context():
    db.create_all()

    is_librarian_present = db.session.query(Librarian.id).first() is not None
    if not is_librarian_present:
        librarian = Librarian(
            id=10000,
            username="librarian",
            email="librarian@email.com",
            passhash=generate_password_hash("12QWasZX"),
            name="Librarian",
        )
        db.session.add(librarian)
        db.session.commit()
        print("Librarian created")
