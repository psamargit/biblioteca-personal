"""
Modelo de Préstamo
"""
from datetime import datetime, timedelta
from app import db


class Loan(db.Model):
    """Modelo de préstamo de libros"""

    __tablename__ = 'loans'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Información del préstamo
    borrower_name = db.Column(db.String(150), nullable=False)
    borrower_email = db.Column(db.String(120))
    borrower_phone = db.Column(db.String(20))

    # Fechas
    loan_date = db.Column(db.Date, default=datetime.utcnow().date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date)

    # Estado
    returned = db.Column(db.Boolean, default=False, nullable=False)
    notes = db.Column(db.Text)

    # Metadatos
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Loan {self.borrower_name} - {self.book.title if self.book else "Unknown"}>'

    @property
    def is_overdue(self):
        """Verifica si el préstamo está vencido"""
        if self.returned:
            return False
        return datetime.utcnow().date() > self.due_date

    @property
    def days_overdue(self):
        """Retorna los días de retraso"""
        if not self.is_overdue:
            return 0
        return (datetime.utcnow().date() - self.due_date).days

    @property
    def days_until_due(self):
        """Retorna los días hasta la fecha de vencimiento"""
        if self.returned:
            return 0
        delta = self.due_date - datetime.utcnow().date()
        return delta.days

    @property
    def loan_duration(self):
        """Retorna la duración del préstamo en días"""
        end_date = self.return_date if self.returned else datetime.utcnow().date()
        return (end_date - self.loan_date).days

    def mark_as_returned(self):
        """Marca el préstamo como devuelto"""
        self.returned = True
        self.return_date = datetime.utcnow().date()
        db.session.commit()

    def to_dict(self):
        """Convierte el préstamo a diccionario"""
        return {
            'id': self.id,
            'book_id': self.book_id,
            'book_title': self.book.title if self.book else None,
            'borrower_name': self.borrower_name,
            'borrower_email': self.borrower_email,
            'borrower_phone': self.borrower_phone,
            'loan_date': self.loan_date.isoformat(),
            'due_date': self.due_date.isoformat(),
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'returned': self.returned,
            'is_overdue': self.is_overdue,
            'days_overdue': self.days_overdue,
            'days_until_due': self.days_until_due,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
