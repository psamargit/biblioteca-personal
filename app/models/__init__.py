"""
Modelos de la aplicación
"""
from .user import User
from .book import Book, book_tags
from .tag import Tag
from .wishlist import WishlistItem
from .loan import Loan

__all__ = ['User', 'Book', 'Tag', 'WishlistItem', 'Loan', 'book_tags']
