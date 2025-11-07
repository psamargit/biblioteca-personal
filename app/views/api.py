"""
Vistas de API para integraciones externas
"""
import requests
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/google-books/<isbn>')
@login_required
def google_books_lookup(isbn):
    """
    Buscar información de un libro en Google Books API por ISBN

    Returns:
        JSON con información del libro o error
    """
    try:
        # API de Google Books
        api_key = current_app.config.get('GOOGLE_BOOKS_API_KEY', '')
        url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}'

        if api_key:
            url += f'&key={api_key}'

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get('totalItems', 0) == 0:
            return jsonify({
                'success': False,
                'error': 'No se encontró información para este ISBN'
            }), 404

        # Extraer información del primer resultado
        book_info = data['items'][0]['volumeInfo']

        result = {
            'success': True,
            'data': {
                'title': book_info.get('title', ''),
                'authors': ', '.join(book_info.get('authors', [])),
                'publisher': book_info.get('publisher', ''),
                'publication_year': book_info.get('publishedDate', '')[:4] if book_info.get('publishedDate') else None,
                'description': book_info.get('description', ''),
                'genre': ', '.join(book_info.get('categories', [])),
                'cover_image': book_info.get('imageLinks', {}).get('thumbnail', ''),
                'isbn': isbn
            }
        }

        return jsonify(result)

    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Error al conectar con Google Books: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error inesperado: {str(e)}'
        }), 500


@bp.route('/search-books')
@login_required
def search_books_api():
    """
    Buscar libros en Google Books por título o autor

    Query params:
        q: Texto de búsqueda

    Returns:
        JSON con resultados de búsqueda
    """
    query = request.args.get('q', '')

    if not query or len(query) < 3:
        return jsonify({
            'success': False,
            'error': 'La búsqueda debe tener al menos 3 caracteres'
        }), 400

    try:
        api_key = current_app.config.get('GOOGLE_BOOKS_API_KEY', '')
        url = f'https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=10'

        if api_key:
            url += f'&key={api_key}'

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get('totalItems', 0) == 0:
            return jsonify({
                'success': True,
                'results': []
            })

        # Extraer información relevante
        results = []
        for item in data.get('items', []):
            book_info = item.get('volumeInfo', {})
            isbn_list = book_info.get('industryIdentifiers', [])
            isbn = next((id['identifier'] for id in isbn_list if id['type'] in ['ISBN_13', 'ISBN_10']), '')

            results.append({
                'title': book_info.get('title', ''),
                'authors': ', '.join(book_info.get('authors', [])),
                'publisher': book_info.get('publisher', ''),
                'publication_year': book_info.get('publishedDate', '')[:4] if book_info.get('publishedDate') else None,
                'description': book_info.get('description', ''),
                'genre': ', '.join(book_info.get('categories', [])),
                'cover_image': book_info.get('imageLinks', {}).get('thumbnail', ''),
                'isbn': isbn
            })

        return jsonify({
            'success': True,
            'results': results
        })

    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Error al conectar con Google Books: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error inesperado: {str(e)}'
        }), 500
