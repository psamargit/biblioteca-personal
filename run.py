#!/usr/bin/env python3
"""
Script principal para ejecutar la aplicación
"""
import os
from app import create_app, db
from app.models import User, Book, Tag, Loan, WishlistItem

# Crear la aplicación
app = create_app(os.getenv('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    """
    Registra variables para el shell de Flask
    Esto permite usar 'flask shell' con acceso directo a los modelos
    """
    return {
        'db': db,
        'User': User,
        'Book': Book,
        'Tag': Tag,
        'Loan': Loan,
        'WishlistItem': WishlistItem
    }


if __name__ == '__main__':
    # Solo para desarrollo. En producción usar gunicorn
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', 'True') == 'True'
    )
