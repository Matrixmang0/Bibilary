from app import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(14), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    passhash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(120), nullable=False)

class Librarian(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(14), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    passhash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(120), nullable=False)

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)
    image = db.Column(db.LargeBinary, nullable=True)
    description = db.Column(db.String(1024), nullable=False)
    books = db.relationship('Book', backref='genre', lazy=True)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    authors = db.Column(db.String(120), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=False)
    image = db.Column(db.LargeBinary, nullable=True)
    content = db.Column(db.LargeBinary, nullable=False)
    genre = db.relationship('Genre', backref='book', lazy=True)
    
class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    date_requested = db.Column(db.DateTime, nullable=False)
    days_requested = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', backref='request', lazy=True)
    book = db.relationship('Book', backref='request', lazy=True)

class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    date_issued = db.Column(db.DateTime, nullable=False)
    date_due = db.Column(db.DateTime, nullable=False)
    remaining_days = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', backref='borrow', lazy=True)

with app.app_context():
    db.create_all()