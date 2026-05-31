from datetime import datetime, timedelta
from extensions import db


class Book(db.Model):
    __tablename__ = 'books'

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    author      = db.Column(db.String(100), nullable=False)
    isbn        = db.Column(db.String(20), unique=True, nullable=True)
    genre       = db.Column(db.String(50), nullable=True)
    quantity    = db.Column(db.Integer, default=1)
    available   = db.Column(db.Integer, default=1)
    added_on    = db.Column(db.DateTime, default=datetime.utcnow)

    transactions = db.relationship('Transaction', backref='book', lazy=True)

    def __repr__(self):
        return f'<Book {self.title}>'

    @property
    def is_available(self):
        return self.available > 0


class Member(db.Model):
    __tablename__ = 'members'

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    phone      = db.Column(db.String(15), nullable=True)
    address    = db.Column(db.Text, nullable=True)
    joined_on  = db.Column(db.DateTime, default=datetime.utcnow)
    is_active  = db.Column(db.Boolean, default=True)

    transactions = db.relationship('Transaction', backref='member', lazy=True)

    def __repr__(self):
        return f'<Member {self.name}>'

    @property
    def active_borrows(self):
        return Transaction.query.filter_by(
            member_id=self.id,
            return_date=None
        ).count()

    @property
    def total_fine_due(self):
        unpaid = Transaction.query.filter_by(
            member_id=self.id,
            paid=False
        ).all()
        return sum(t.calculate_fine() for t in unpaid)


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id          = db.Column(db.Integer, primary_key=True)
    book_id     = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    member_id   = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    issue_date  = db.Column(db.DateTime, default=datetime.utcnow)
    due_date    = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=14))
    return_date = db.Column(db.DateTime, nullable=True)
    fine        = db.Column(db.Float, default=0.0)
    paid        = db.Column(db.Boolean, default=False)

    FINE_PER_DAY = 2.0  # ₹2 per day

    def __repr__(self):
        return f'<Transaction book={self.book_id} member={self.member_id}>'

    @property
    def is_returned(self):
        return self.return_date is not None

    @property
    def is_overdue(self):
        if self.is_returned:
            return False
        return datetime.utcnow() > self.due_date

    def calculate_fine(self):
        check_date = self.return_date or datetime.utcnow()
        if check_date > self.due_date:
            days_late = (check_date - self.due_date).days
            return round(days_late * self.FINE_PER_DAY, 2)
        return 0.0

    def close(self):
        """Call this when a book is returned."""
        self.return_date = datetime.utcnow()
        self.fine = self.calculate_fine()
        self.book.available += 1