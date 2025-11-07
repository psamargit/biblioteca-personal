"""
Modelo de Usuario
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Model):
    """Modelo de usuario para autenticación"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)

    # Relaciones
    books = db.relationship('Book', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    loans = db.relationship('Loan', backref='lender', lazy='dynamic', cascade='all, delete-orphan')
    wishlist_items = db.relationship('WishlistItem', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """
        Hashea y guarda la contraseña

        Args:
            password: Contraseña en texto plano
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verifica si la contraseña es correcta

        Args:
            password: Contraseña en texto plano

        Returns:
            bool: True si la contraseña es correcta
        """
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """Actualiza la fecha del último login"""
        self.last_login = datetime.utcnow()
        db.session.commit()

    @property
    def total_books(self):
        """Retorna el total de libros del usuario"""
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


@login_manager.user_loader
def load_user(user_id):
    """
    Callback para Flask-Login para cargar un usuario

    Args:
        user_id: ID del usuario

    Returns:
        User: Instancia del usuario o None
    """
    return User.query.get(int(user_id))
