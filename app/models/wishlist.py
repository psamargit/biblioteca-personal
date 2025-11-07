"""
Modelo de Lista de Deseos
"""
from datetime import datetime
from app import db


class WishlistItem(db.Model):
    """Modelo de elemento de lista de deseos (libros por comprar)"""

    __tablename__ = 'wishlist_items'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    authors = db.Column(db.String(255))
    isbn = db.Column(db.String(20))
    publisher = db.Column(db.String(150))
    estimated_price = db.Column(db.Float)
    priority = db.Column(db.Integer, default=3)  # 1=Alta, 2=Media, 3=Baja
    notes = db.Column(db.Text)
    url = db.Column(db.String(500))  # URL donde se puede comprar
    acquired = db.Column(db.Boolean, default=False, nullable=False)
    acquired_date = db.Column(db.Date)

    # Metadatos
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<WishlistItem {self.title}>'

    @property
    def priority_text(self):
        """Retorna el texto de la prioridad"""
        priorities = {1: 'Alta', 2: 'Media', 3: 'Baja'}
        return priorities.get(self.priority, 'Media')

    @property
    def priority_badge_class(self):
        """Retorna la clase CSS para el badge de prioridad"""
        classes = {1: 'danger', 2: 'warning', 3: 'secondary'}
        return classes.get(self.priority, 'secondary')

    def to_dict(self):
        """Convierte el item a diccionario"""
        return {
            'id': self.id,
            'title': self.title,
            'authors': self.authors,
            'isbn': self.isbn,
            'publisher': self.publisher,
            'estimated_price': self.estimated_price,
            'priority': self.priority,
            'priority_text': self.priority_text,
            'notes': self.notes,
            'url': self.url,
            'acquired': self.acquired,
            'acquired_date': self.acquired_date.isoformat() if self.acquired_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
