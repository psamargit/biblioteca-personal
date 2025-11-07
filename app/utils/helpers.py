"""
Funciones de utilidad
"""
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
from app import db


def allowed_file(filename, allowed_extensions=None):
    """
    Verifica si el archivo tiene una extensión permitida

    Args:
        filename: Nombre del archivo
        allowed_extensions: Set de extensiones permitidas

    Returns:
        bool: True si la extensión es válida
    """
    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', set())

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_cover_image(file):
    """
    Guarda una imagen de portada y retorna el path relativo

    Args:
        file: Archivo de imagen de werkzeug

    Returns:
        str: Path relativo de la imagen guardada o None si falla
    """
    if file and allowed_file(file.filename):
        # Generar nombre único
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"

        # Guardar archivo
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        # Retornar path relativo para la URL
        return f"uploads/covers/{filename}"

    return None


def delete_cover_image(cover_path):
    """
    Elimina una imagen de portada del sistema de archivos

    Args:
        cover_path: Path relativo de la imagen

    Returns:
        bool: True si se eliminó correctamente
    """
    if not cover_path or cover_path.startswith('http'):
        return False

    try:
        filepath = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            os.path.basename(cover_path)
        )
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception as e:
        current_app.logger.error(f"Error eliminando imagen: {e}")

    return False


def format_date(date, format='%d/%m/%Y'):
    """
    Formatea una fecha para mostrar

    Args:
        date: Objeto date o datetime
        format: Formato de fecha

    Returns:
        str: Fecha formateada o string vacío
    """
    if date is None:
        return ''

    if isinstance(date, str):
        try:
            date = datetime.fromisoformat(date)
        except:
            return date

    try:
        return date.strftime(format)
    except:
        return str(date)


def truncate_text(text, length=100, suffix='...'):
    """
    Trunca un texto a una longitud específica

    Args:
        text: Texto a truncar
        length: Longitud máxima
        suffix: Sufijo a agregar si se trunca

    Returns:
        str: Texto truncado
    """
    if not text:
        return ''

    if len(text) <= length:
        return text

    return text[:length].rsplit(' ', 1)[0] + suffix


def parse_csv_date(date_str, formats=None):
    """
    Intenta parsear una fecha de CSV en múltiples formatos

    Args:
        date_str: String con la fecha
        formats: Lista de formatos a intentar

    Returns:
        date: Objeto date o None si falla
    """
    if not date_str:
        return None

    if formats is None:
        formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%m/%d/%Y',
            '%Y/%m/%d'
        ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    return None


def sanitize_isbn(isbn):
    """
    Sanitiza un ISBN removiendo espacios y guiones

    Args:
        isbn: String con ISBN

    Returns:
        str: ISBN sanitizado
    """
    if not isbn:
        return ''

    return ''.join(c for c in isbn if c.isalnum())


def get_book_stats(user):
    """
    Obtiene estadísticas de libros de un usuario

    Args:
        user: Objeto User

    Returns:
        dict: Diccionario con estadísticas
    """
    from app.models import Book
    from sqlalchemy import func

    books = Book.query.filter_by(user_id=user.id)

    stats = {
        'total': books.count(),
        'physical': books.filter_by(book_type='physical').count(),
        'digital': books.filter_by(book_type='digital').count(),
        'read': books.filter_by(status='read').count(),
        'reading': books.filter_by(status='reading').count(),
        'unread': books.filter_by(status='unread').count(),
    }

    # Top géneros
    genre_stats = db.session.query(
        Book.genre,
        func.count(Book.id).label('count')
    ).filter(
        Book.user_id == user.id,
        Book.genre.isnot(None)
    ).group_by(Book.genre).order_by(
        func.count(Book.id).desc()
    ).limit(5).all()

    stats['top_genres'] = [{'genre': g[0], 'count': g[1]} for g in genre_stats]

    return stats
