from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Book

books_bp = Blueprint('books', __name__)

@books_bp.route('/')
def list_books():
    query = request.args.get('q', '')
    if query:
        books = Book.query.filter(
            Book.title.ilike(f'%{query}%') |
            Book.author.ilike(f'%{query}%')
        ).all()
    else:
        books = Book.query.all()
    return render_template('books/list.html', books=books, query=query)

@books_bp.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        book = Book(
            title=request.form['title'],
            author=request.form['author'],
            isbn=request.form.get('isbn'),
            genre=request.form.get('genre'),
            quantity=int(request.form.get('quantity', 1)),
            available=int(request.form.get('quantity', 1))
        )
        db.session.add(book)
        db.session.commit()
        flash('Book added successfully.', 'success')
        return redirect(url_for('books.list_books'))
    return render_template('books/add.html')

@books_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.isbn = request.form.get('isbn')
        book.genre = request.form.get('genre')
        book.quantity = int(request.form.get('quantity', 1))
        db.session.commit()
        flash('Book updated.', 'success')
        return redirect(url_for('books.list_books'))
    return render_template('books/add.html', book=book)

@books_bp.route('/delete/<int:id>')
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted.', 'success')
    return redirect(url_for('books.list_books'))