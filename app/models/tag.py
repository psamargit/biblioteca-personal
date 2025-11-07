"""
Modelo de Etiqueta
"""
from datetime import datetime
from app import db


class Tag(db.Model):
    """Modelo de etiqueta para organizar libros"""

    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)
    color = db.Column(db.String(7), default='#007bff')  # Color hexadecimal para la etiqueta
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Tag {self.name}>'

    @property
    def book_count(self):
        """Retorna el número de libros con esta etiqueta"""
        return len(self.books)

    def to_dict(self):
        """Convierte la etiqueta a diccionario"""
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'description': self.description,
            'book_count': self.book_count,
            'created_at': self.created_at.isoformat()
        }
