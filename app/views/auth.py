"""
Vistas de autenticación
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión"""
    # Si ya está autenticado, redirigir al dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()

    if form.validate_on_submit():
        # Buscar usuario
        user = User.query.filter_by(username=form.username.data).first()

        # Verificar credenciales
        if user is None or not user.check_password(form.password.data):
            flash('Usuario o contraseña incorrectos', 'danger')
            return redirect(url_for('auth.login'))

        # Verificar que el usuario esté activo
        if not user.is_active:
            flash('Tu cuenta ha sido desactivada', 'warning')
            return redirect(url_for('auth.login'))

        # Iniciar sesión
        login_user(user, remember=form.remember_me.data)
        user.update_last_login()

        # Redirigir a la página solicitada o al dashboard
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('dashboard.index')

        flash(f'Bienvenido, {user.username}!', 'success')
        return redirect(next_page)

    return render_template('auth/login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    # Si ya está autenticado, redirigir al dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        # Crear nuevo usuario
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@bp.route('/logout')
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('auth.login'))
