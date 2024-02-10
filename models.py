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
    requests = db.relationship("Request", backref="user", lazy=True)
    borrows = db.relationship("Borrow", backref="user", lazy=True)


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
    image = db.Column(db.LargeBinary, nullable=True)
    description = db.Column(db.String, nullable=False)
    books = db.relationship("Book", backref="genre", lazy=True)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    authors = db.Column(db.String(120), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"), nullable=False)
    image = db.Column(db.LargeBinary, nullable=True)
    content = db.Column(db.LargeBinary, nullable=False)
    requests = db.relationship("Request", backref="book", lazy=True)
    borrows = db.relationship("Borrow", backref="book", lazy=True)


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
    remaining_days = db.Column(db.Integer, nullable=False)


with app.app_context():
    db.create_all()

    is_librarian_present = db.session.query(Librarian.id).first() is not None
    if not is_librarian_present:
        librarian = Librarian(
            id=10000,
            username="librarian",
            email="librarian@email.com",
            passhash=generate_password_hash("1234"),
            name="Librarian",
        )
        db.session.add(librarian)
        db.session.commit()
        print("Librarian created")
