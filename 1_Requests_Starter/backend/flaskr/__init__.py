import os
from flask import Flask, request, abort, jsonify
from models import setup_db, Book
from flask_sqlalchemy import SQLAlchemy  # , or_
from flask_cors import CORS
import random


BOOKS_PER_SHELF = 8


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    @app.get('/books')
    def get_books():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * BOOKS_PER_SHELF
        end = start + BOOKS_PER_SHELF

        books = Book.query.all()
        formatted_books = [book.format() for book in books]
        return jsonify({
            'success': True,
            'books': formatted_books[start:end],
            'total_books': len(formatted_books)
        })

    @app.patch('/books/<int:book_id>')
    def update_rating(book_id):
        book = Book.query.filter(Book.id == book_id).first_or_404()
        updates = request.get_json()
        book.rating = updates["rating"]
        book.update()

        return jsonify({
            'success': True
        })

    @app.delete('/books/<int:book_id>')
    def delete_book(book_id):
        book = Book.query.filter(Book.id == book_id).one_or_none()
        book.delete()

        page = request.args.get('page', 1, type=int)
        start = (page - 1) * BOOKS_PER_SHELF
        end = start + BOOKS_PER_SHELF

        books = Book.query.all()
        formatted_books = [book.format() for book in books]
        return jsonify({
            'success': True,
            'deleted': book_id,
            'books': formatted_books[start:end],
            'total_books': len(formatted_books)
        })

    @app.post('/books')
    def add_book():
        form = request.get_json()
        book = Book(
            title=form["title"],
            author=form["author"],
            rating=form["rating"]
        )
        book.insert()

        page = request.args.get('page', 1, type=int)
        start = (page - 1) * BOOKS_PER_SHELF
        end = start + BOOKS_PER_SHELF

        books = Book.query.all()
        formatted_books = [book.format() for book in books]
        return jsonify({
            'success': True,
            'created': book.id,
            'books': formatted_books[start:end],
            'total_books': len(formatted_books)
        })

    return app
