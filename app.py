from flask import Flask, render_template
from extensions import db
from models import Book, Member, Transaction


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'change-this-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from routes.books import books_bp
    from routes.members import members_bp
    from routes.transactions import transactions_bp
    app.register_blueprint(books_bp, url_prefix='/books')
    app.register_blueprint(members_bp, url_prefix='/members')
    app.register_blueprint(transactions_bp, url_prefix='/transactions')

    @app.route('/')
    def index():
        total_books = Book.query.count()
        total_members = Member.query.count()
        active_borrows = Transaction.query.filter_by(return_date=None).count()
        overdue = sum(1 for t in Transaction.query.filter_by(return_date=None).all() if t.is_overdue)
        return render_template('index.html',
            total_books=total_books,
            total_members=total_members,
            active_borrows=active_borrows,
            overdue=overdue)

    with app.app_context():
        db.create_all()

    return app