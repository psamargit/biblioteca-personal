"""
Vistas del dashboard
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models import Book, Loan, WishlistItem, Tag

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@bp.route('/')
@login_required
def index():
    """Dashboard principal con estadísticas"""

    # Estadísticas de libros
    total_books = Book.query.filter_by(user_id=current_user.id).count()
    physical_books = Book.query.filter_by(user_id=current_user.id, book_type='physical').count()
    digital_books = Book.query.filter_by(user_id=current_user.id, book_type='digital').count()
    books_read = Book.query.filter_by(user_id=current_user.id, status='read').count()
    books_reading = Book.query.filter_by(user_id=current_user.id, status='reading').count()
    books_unread = Book.query.filter_by(user_id=current_user.id, status='unread').count()

    # Estadísticas de préstamos
    active_loans = Loan.query.join(Book).filter(
        Book.user_id == current_user.id,
        Loan.returned == False
    ).count()

    overdue_loans = Loan.query.join(Book).filter(
        Book.user_id == current_user.id,
        Loan.returned == False
    ).filter(
        Loan.due_date < db.func.current_date()
    ).count()

    # Lista de deseos
    wishlist_count = WishlistItem.query.filter_by(
        user_id=current_user.id,
        acquired=False
    ).count()

    # Top 5 géneros
    top_genres = db.session.query(
        Book.genre,
        func.count(Book.id).label('count')
    ).filter(
        Book.user_id == current_user.id,
        Book.genre.isnot(None),
        Book.genre != ''
    ).group_by(Book.genre).order_by(
        func.count(Book.id).desc()
    ).limit(5).all()

    # Libros agregados recientemente
    recent_books = Book.query.filter_by(
        user_id=current_user.id
    ).order_by(Book.created_at.desc()).limit(5).all()

    # Préstamos activos
    recent_loans = Loan.query.join(Book).filter(
        Book.user_id == current_user.id,
        Loan.returned == False
    ).order_by(Loan.loan_date.desc()).limit(5).all()

    # Items de wishlist con alta prioridad
    high_priority_wishlist = WishlistItem.query.filter_by(
        user_id=current_user.id,
        acquired=False,
        priority=1
    ).order_by(WishlistItem.created_at.desc()).limit(5).all()

    stats = {
        'total_books': total_books,
        'physical_books': physical_books,
        'digital_books': digital_books,
        'books_read': books_read,
        'books_reading': books_reading,
        'books_unread': books_unread,
        'active_loans': active_loans,
        'overdue_loans': overdue_loans,
        'wishlist_count': wishlist_count,
        'top_genres': top_genres,
        'recent_books': recent_books,
        'recent_loans': recent_loans,
        'high_priority_wishlist': high_priority_wishlist
    }

    return render_template('dashboard/index.html', stats=stats)
