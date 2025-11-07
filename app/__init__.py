"""
Inicialización de la aplicación Flask
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config.config import config

# Inicialización de extensiones
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app(config_name=None):
    """
    Factory para crear la aplicación Flask

    Args:
        config_name: Nombre de la configuración a usar ('development', 'production', 'testing')

    Returns:
        app: Instancia de la aplicación Flask
    """
    # Crear instancia de Flask
    app = Flask(__name__)

    # Cargar configuración
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app.config.from_object(config[config_name])

    # Inicializar extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Configurar Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'

    # Crear directorio de uploads si no existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Crear directorio de instance si no existe
    instance_path = os.path.join(app.root_path, '..', 'instance')
    os.makedirs(instance_path, exist_ok=True)

    # Registrar blueprints
    from app.views import auth, books, dashboard, loans, wishlist, api

    app.register_blueprint(auth.bp)
    app.register_blueprint(books.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(loans.bp)
    app.register_blueprint(wishlist.bp)
    app.register_blueprint(api.bp)

    # Registrar comandos CLI personalizados
    from app.commands import init_db_command, create_admin_command
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_command)

    # Context processor para hacer disponibles funciones en templates
    @app.context_processor
    def utility_processor():
        """Funciones disponibles en todos los templates"""
        from app.utils.helpers import format_date, truncate_text
        return dict(
            format_date=format_date,
            truncate_text=truncate_text
        )

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        return render_template('errors/403.html'), 403

    return app
