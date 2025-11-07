"""
Modelo de Propietario (miembro de la familia)
"""
from datetime import datetime
from app import db


class Owner(db.Model):
    """Modelo de propietario para asignar libros a miembros de la familia"""

    __tablename__ = 'owners'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    relationship = db.Column(db.String(50))  # Padre, Madre, Hijo, Hija, etc.
    color = db.Column(db.String(7), default='#007bff')  # Color para identificación visual
    email = db.Column(db.String(120))
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Metadatos
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relaciones
    books = db.relationship('Book', backref='owner', lazy='dynamic')

    def __repr__(self):
        return f'<Owner {self.name}>'

    @property
    def total_books(self):
        """Retorna el total de libros del propietario"""
        return self.books.count()

    @property
    def books_read(self):
        """Retorna el total de libros leídos"""
        return self.books.filter_by(status='read').count()

    @property
    def books_reading(self):
        """Retorna el total de libros en lectura"""
        return self.books.filter_by(status='reading').count()

    @property
    def physical_books(self):
        """Retorna el total de libros físicos"""
        return self.books.filter_by(book_type='physical').count()

    @property
    def digital_books(self):
        """Retorna el total de libros digitales"""
        return self.books.filter_by(book_type='digital').count()

    def to_dict(self):
        """Convierte el propietario a diccionario"""
        return {
            'id': self.id,
            'name': self.name,
            'relationship': self.relationship,
            'color': self.color,
            'email': self.email,
            'notes': self.notes,
            'is_active': self.is_active,
            'total_books': self.total_books,
            'books_read': self.books_read,
            'books_reading': self.books_reading,
            'physical_books': self.physical_books,
            'digital_books': self.digital_books,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
