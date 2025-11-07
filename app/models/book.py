"""
Modelo de Libro
"""
from datetime import datetime
from app import db

# Tabla de asociación many-to-many entre libros y etiquetas
book_tags = db.Table('book_tags',
    db.Column('book_id', db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


class Book(db.Model):
    """Modelo de libro para el inventario"""

    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)

    # Información básica
    title = db.Column(db.String(255), nullable=False, index=True)
    authors = db.Column(db.String(255), nullable=False)  # Separados por coma
    isbn = db.Column(db.String(20), unique=True, index=True)
    publisher = db.Column(db.String(150))
    publication_year = db.Column(db.Integer)

    # Categorización
    genre = db.Column(db.String(100), index=True)
    book_type = db.Column(db.String(20), nullable=False, default='physical', index=True)  # physical/digital

    # Estado y ubicación
    status = db.Column(db.String(20), nullable=False, default='unread', index=True)  # unread/reading/read
    location = db.Column(db.String(150))  # Para físicos: estante, caja, etc.
    format = db.Column(db.String(50))  # Para digitales: PDF, EPUB, MOBI, etc.

    # Información adicional
    cover_image = db.Column(db.String(255))  # URL o path de la imagen
    notes = db.Column(db.Text)
    acquisition_date = db.Column(db.Date)
    price = db.Column(db.Float)

    # Búsqueda de texto completo
    description = db.Column(db.Text)

    # Metadatos
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relaciones
    tags = db.relationship('Tag', secondary=book_tags, lazy='subquery',
                          backref=db.backref('books', lazy=True))
    loans = db.relationship('Loan', backref='book', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Book {self.title}>'

    def to_dict(self):
        """
        Convierte el libro a diccionario para JSON

        Returns:
            dict: Diccionario con los datos del libro
        """
        return {
            'id': self.id,
            'title': self.title,
            'authors': self.authors,
            'isbn': self.isbn,
            'publisher': self.publisher,
            'publication_year': self.publication_year,
            'genre': self.genre,
            'book_type': self.book_type,
            'status': self.status,
            'location': self.location,
            'format': self.format,
            'cover_image': self.cover_image,
            'notes': self.notes,
            'acquisition_date': self.acquisition_date.isoformat() if self.acquisition_date else None,
            'price': self.price,
            'description': self.description,
            'tags': [tag.name for tag in self.tags],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @property
    def authors_list(self):
        """Retorna la lista de autores separados"""
        return [author.strip() for author in self.authors.split(',')] if self.authors else []

    @property
    def is_available(self):
        """Verifica si el libro está disponible (no prestado)"""
        active_loan = self.loans.filter_by(returned=False).first()
        return active_loan is None

    @property
    def current_loan(self):
        """Retorna el préstamo activo si existe"""
        return self.loans.filter_by(returned=False).first()

    @staticmethod
    def search(query, filters=None, user_id=None):
        """
        Búsqueda avanzada de libros

        Args:
            query: Texto a buscar
            filters: Diccionario con filtros adicionales
            user_id: ID del usuario para filtrar sus libros

        Returns:
            Query: Query de SQLAlchemy para ejecutar
        """
        books_query = Book.query

        # Filtrar por usuario si se proporciona
        if user_id:
            books_query = books_query.filter_by(user_id=user_id)

        # Búsqueda de texto
        if query:
            search_filter = db.or_(
                Book.title.ilike(f'%{query}%'),
                Book.authors.ilike(f'%{query}%'),
                Book.isbn.ilike(f'%{query}%'),
                Book.publisher.ilike(f'%{query}%'),
                Book.description.ilike(f'%{query}%'),
                Book.notes.ilike(f'%{query}%')
            )
            books_query = books_query.filter(search_filter)

        # Aplicar filtros adicionales
        if filters:
            if 'genre' in filters and filters['genre']:
                books_query = books_query.filter_by(genre=filters['genre'])

            if 'book_type' in filters and filters['book_type']:
                books_query = books_query.filter_by(book_type=filters['book_type'])

            if 'status' in filters and filters['status']:
                books_query = books_query.filter_by(status=filters['status'])

            if 'author' in filters and filters['author']:
                books_query = books_query.filter(Book.authors.ilike(f'%{filters["author"]}%'))

            if 'year_from' in filters and filters['year_from']:
                books_query = books_query.filter(Book.publication_year >= filters['year_from'])

            if 'year_to' in filters and filters['year_to']:
                books_query = books_query.filter(Book.publication_year <= filters['year_to'])

        return books_query
