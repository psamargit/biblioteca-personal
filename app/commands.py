"""
Comandos CLI personalizados para Flask
"""
import click
from flask.cli import with_appcontext
from app import db
from app.models import User, Book, Tag, Loan, WishlistItem


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Inicializa la base de datos creando todas las tablas."""
    db.create_all()
    click.echo('Base de datos inicializada.')


@click.command('create-admin')
@click.option('--username', prompt='Usuario', help='Nombre de usuario')
@click.option('--email', prompt='Email', help='Correo electrónico')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Contraseña')
@with_appcontext
def create_admin_command(username, email, password):
    """Crea un usuario administrador."""
    # Verificar si el usuario ya existe
    if User.query.filter_by(username=username).first():
        click.echo(f'Error: El usuario {username} ya existe.', err=True)
        return

    if User.query.filter_by(email=email).first():
        click.echo(f'Error: El email {email} ya está registrado.', err=True)
        return

    # Crear usuario
    user = User(username=username, email=email, is_admin=True)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    click.echo(f'Usuario administrador {username} creado exitosamente.')
