from flask_restful import Resource, Api
from app import app
from models import User, Librarian, Genre, Book, Request, Borrow, Purchase, db
from flask import request
import datetime

api = Api(app)

class UserAPI(Resource):
    def get(self, user_id):
        users = User.query.filter_by(id=user_id).all()
        if users == []:
            return {"message": "User not found"}, 404
        return {
            "users": [
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "username": user.username,
                }
                for user in users
            ]
        }


class LibrarianAPI(Resource):
    def get(self, librarian_id):
        librarians = Librarian.query.filter_by(id=librarian_id).all()
        if librarians == []:
            return {"message": "Librarian not found"}, 404
        return {
            "librarian": [
                {
                    "id": librarian.id,
                    "name": librarian.name,
                    "email": librarian.email,
                    "username": librarian.username,
                }
                for librarian in librarians
            ]
        }


class GenreAPI(Resource):
    def get(self, genre_id):
        genres = Genre.query.filter_by(id=genre_id).all()
        if genres == []:
            return {"message": "Genre not found"}, 404
        return {
            "genre": [
                {
                    "id": genre.id,
                    "name": genre.name,
                    "description": genre.description,
                }
                for genre in genres
            ]
        }

    def post(self, genre_id):
        args = request.get_json()
        name = args.get("name")
        description = args.get("description")
        if Genre.query.filter_by(name=name).first():
            return {"message": "Genre already exists"}, 400
        if not name or not description:
            return {"message": "Name and description are required"}, 400
        new_genre = Genre(
            name=name, description=description, date_created=datetime.datetime.now()
        )
        db.session.add(new_genre)
        db.session.commit()
        return {"message": "Genre added successfully"}, 201

    def put(self, genre_id):
        args = request.get_json()
        genre = Genre.query.filter_by(id=genre_id).first()
        if not genre:
            return {"message": "Genre not found"}, 404
        if "name" not in args and "description" in args:
            genre.description = args.get("description", genre.description)
        elif "name" in args and "description" not in args:
            genre.name = args.get("name", genre.name)
        elif "name" in args and "description" in args:
            genre.name = args.get("name", genre.name)
            genre.description = args.get("description", genre.description)
        db.session.commit()
        return {"message": "Genre updated successfully"}, 200

    def delete(self, genre_id):
        genre = Genre.query.filter_by(id=genre_id).first()
        if not genre:
            return {"message": "Genre not found"}, 404
        db.session.delete(genre)
        db.session.commit()
        return {"message": "Genre deleted successfully"}, 200


class BookAPI(Resource):
    def get(self, book_id):
        books = Book.query.filter_by(id=book_id).all()
        if books == []:
            return {"message": "Book not found"}, 404
        return {
            "book": [
                {
                    "id": book.id,
                    "title": book.title,
                    "authors": book.authors,
                    "price": book.price,
                    "quantity": book.quantity,
                    "summary": book.summary,
                }
                for book in books
            ]
        }


class RequestAPI(Resource):
    def get(self, request_id):
        requests = Request.query.filter_by(id=request_id).all()
        if requests == []:
            return {"message": "Request not found"}, 404
        return {
            "request": [
                {
                    "id": request.id,
                    "user_id": request.user_id,
                    "book_id": request.book_id,
                }
                for request in requests
            ]
        }


class BorrowAPI(Resource):
    def get(self, borrow_id):
        borrows = Borrow.query.filter_by(id=borrow_id).all()
        if borrows == []:
            return {"message": "Borrow not found"}, 404
        return {
            "borrow": [
                {"id": borrow.id, "user_id": borrow.user_id, "book_id": borrow.book_id}
                for borrow in borrows
            ]
        }


class PurchaseAPI(Resource):
    def get(self, purchase_id):
        purchases = Purchase.query.filter_by(id=purchase_id).all()
        if purchases == []:
            return {"message": "Purchase not found"}, 404
        return {
            "purchase": [
                {
                    "id": purchase.id,
                    "user_id": purchase.user_id,
                    "book_id": purchase.book_id,
                }
                for purchase in purchases
            ]
        }


api.add_resource(UserAPI, "/api/user/<int:user_id>")
api.add_resource(LibrarianAPI, "/api/librarian/<int:librarian_id>")
api.add_resource(GenreAPI, "/api/genre/<int:genre_id>")
api.add_resource(BookAPI, "/api/book/<int:book_id>")
api.add_resource(RequestAPI, "/api/request/<int:request_id>")
api.add_resource(BorrowAPI, "/api/borrow/<int:borrow_id>")
api.add_resource(PurchaseAPI, "/api/purchase/<int:purchase_id>")
