"""
Vistas de propietarios (miembros de la familia)
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Owner
from app.forms import OwnerForm

bp = Blueprint('owners', __name__, url_prefix='/owners')


@bp.route('/')
@login_required
def index():
    """Lista de propietarios"""
    owners = Owner.query.filter_by(user_id=current_user.id).order_by(Owner.name).all()
    return render_template('owners/index.html', owners=owners)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Agregar un nuevo propietario"""
    form = OwnerForm()

    if form.validate_on_submit():
        # Crear propietario
        owner = Owner(
            name=form.name.data,
            relationship=form.relationship.data,
            email=form.email.data,
            color=form.color.data or '#007bff',
            notes=form.notes.data,
            is_active=form.is_active.data,
            user_id=current_user.id
        )

        db.session.add(owner)
        db.session.commit()

        flash(f'Propietario "{owner.name}" agregado exitosamente', 'success')
        return redirect(url_for('owners.index'))

    return render_template('owners/form.html', form=form, title='Agregar Propietario')


@bp.route('/<int:id>')
@login_required
def detail(id):
    """Ver detalles de un propietario y sus libros"""
    owner = Owner.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    # Obtener libros del propietario con paginación
    page = request.args.get('page', 1, type=int)
    pagination = owner.books.order_by(db.text('created_at DESC')).paginate(
        page=page, per_page=20, error_out=False
    )
    books = pagination.items

    # Estadísticas del propietario
    stats = {
        'total_books': owner.total_books,
        'books_read': owner.books_read,
        'books_reading': owner.books_reading,
        'physical_books': owner.physical_books,
        'digital_books': owner.digital_books
    }

    return render_template('owners/detail.html', owner=owner, books=books,
                         pagination=pagination, stats=stats)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar un propietario"""
    owner = Owner.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = OwnerForm(obj=owner)

    if form.validate_on_submit():
        owner.name = form.name.data
        owner.relationship = form.relationship.data
        owner.email = form.email.data
        owner.color = form.color.data or '#007bff'
        owner.notes = form.notes.data
        owner.is_active = form.is_active.data

        db.session.commit()

        flash(f'Propietario "{owner.name}" actualizado exitosamente', 'success')
        return redirect(url_for('owners.detail', id=owner.id))

    return render_template('owners/form.html', form=form, title='Editar Propietario', owner=owner)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Eliminar un propietario"""
    owner = Owner.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    # Verificar si tiene libros asignados
    if owner.total_books > 0:
        flash(f'No se puede eliminar a "{owner.name}" porque tiene {owner.total_books} libros asignados. '
              f'Por favor, reasigna o elimina los libros primero.', 'danger')
        return redirect(url_for('owners.detail', id=owner.id))

    name = owner.name
    db.session.delete(owner)
    db.session.commit()

    flash(f'Propietario "{name}" eliminado exitosamente', 'success')
    return redirect(url_for('owners.index'))


@bp.route('/<int:id>/toggle-active', methods=['POST'])
@login_required
def toggle_active(id):
    """Activar/desactivar un propietario"""
    owner = Owner.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    owner.is_active = not owner.is_active
    db.session.commit()

    status = 'activado' if owner.is_active else 'desactivado'
    flash(f'Propietario "{owner.name}" {status} exitosamente', 'success')

    return redirect(url_for('owners.detail', id=owner.id))
