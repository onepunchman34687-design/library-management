from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Book, Member, Transaction

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/')
def list_transactions():
    transactions = Transaction.query.order_by(Transaction.issue_date.desc()).all()
    return render_template('transactions/list.html', transactions=transactions)

@transactions_bp.route('/issue', methods=['GET', 'POST'])
def issue_book():
    books = Book.query.filter(Book.available > 0).all()
    members = Member.query.filter_by(is_active=True).all()
    if request.method == 'POST':
        book_id = int(request.form['book_id'])
        member_id = int(request.form['member_id'])
        book = Book.query.get_or_404(book_id)
        if book.available < 1:
            flash('This book is not available.', 'danger')
            return redirect(url_for('transactions.issue_book'))
        txn = Transaction(book_id=book_id, member_id=member_id)
        book.available -= 1
        db.session.add(txn)
        db.session.commit()
        flash('Book issued successfully.', 'success')
        return redirect(url_for('transactions.list_transactions'))
    return render_template('transactions/issue.html', books=books, members=members)

@transactions_bp.route('/return/<int:id>')
def return_book(id):
    txn = Transaction.query.get_or_404(id)
    if txn.is_returned:
        flash('Book already returned.', 'warning')
        return redirect(url_for('transactions.list_transactions'))
    txn.close()
    db.session.commit()
    if txn.fine > 0:
        flash(f'Book returned. Fine: ₹{txn.fine}', 'warning')
    else:
        flash('Book returned successfully. No fine.', 'success')
    return redirect(url_for('transactions.list_transactions'))