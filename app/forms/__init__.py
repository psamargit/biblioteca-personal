"""
Formularios de la aplicación
"""
from .auth_forms import LoginForm, RegistrationForm
from .book_forms import BookForm, SearchForm, ImportForm
from .loan_forms import LoanForm
from .wishlist_forms import WishlistItemForm
from .tag_forms import TagForm
from .owner_forms import OwnerForm

__all__ = [
    'LoginForm', 'RegistrationForm',
    'BookForm', 'SearchForm', 'ImportForm',
    'LoanForm', 'WishlistItemForm', 'TagForm', 'OwnerForm'
]
