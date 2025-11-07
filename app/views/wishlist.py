"""
Vistas de lista de deseos
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import WishlistItem
from app.forms import WishlistItemForm

bp = Blueprint('wishlist', __name__, url_prefix='/wishlist')


@bp.route('/')
@login_required
def index():
    """Lista de deseos"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'pending')  # pending, acquired
    priority_filter = request.args.get('priority', '', type=str)

    # Construir query base
    wishlist_query = WishlistItem.query.filter_by(user_id=current_user.id)

    # Aplicar filtros
    if status_filter == 'pending':
        wishlist_query = wishlist_query.filter_by(acquired=False)
    elif status_filter == 'acquired':
        wishlist_query = wishlist_query.filter_by(acquired=True)

    if priority_filter:
        wishlist_query = wishlist_query.filter_by(priority=int(priority_filter))

    # Ordenar por prioridad y fecha de creación
    wishlist_query = wishlist_query.order_by(
        WishlistItem.priority.asc(),
        WishlistItem.created_at.desc()
    )

    # Paginar
    pagination = wishlist_query.paginate(page=page, per_page=20, error_out=False)
    items = pagination.items

    # Calcular precio total estimado de items pendientes
    total_estimated = db.session.query(
        db.func.sum(WishlistItem.estimated_price)
    ).filter(
        WishlistItem.user_id == current_user.id,
        WishlistItem.acquired == False,
        WishlistItem.estimated_price.isnot(None)
    ).scalar() or 0

    return render_template('wishlist/index.html',
                         items=items,
                         pagination=pagination,
                         status_filter=status_filter,
                         priority_filter=priority_filter,
                         total_estimated=total_estimated)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Agregar item a la lista de deseos"""
    form = WishlistItemForm()

    if form.validate_on_submit():
        # Crear item
        item = WishlistItem(
            title=form.title.data,
            authors=form.authors.data,
            isbn=form.isbn.data,
            publisher=form.publisher.data,
            estimated_price=form.estimated_price.data,
            priority=form.priority.data,
            url=form.url.data,
            notes=form.notes.data,
            user_id=current_user.id
        )

        db.session.add(item)
        db.session.commit()

        flash(f'"{item.title}" agregado a tu lista de deseos', 'success')
        return redirect(url_for('wishlist.index'))

    return render_template('wishlist/form.html', form=form, title='Agregar a Lista de Deseos')


@bp.route('/<int:id>')
@login_required
def detail(id):
    """Ver detalles de un item de wishlist"""
    item = WishlistItem.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('wishlist/detail.html', item=item)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar un item de wishlist"""
    item = WishlistItem.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = WishlistItemForm(obj=item)

    if form.validate_on_submit():
        item.title = form.title.data
        item.authors = form.authors.data
        item.isbn = form.isbn.data
        item.publisher = form.publisher.data
        item.estimated_price = form.estimated_price.data
        item.priority = form.priority.data
        item.url = form.url.data
        item.notes = form.notes.data

        db.session.commit()

        flash(f'"{item.title}" actualizado exitosamente', 'success')
        return redirect(url_for('wishlist.detail', id=item.id))

    return render_template('wishlist/form.html', form=form, item=item, title='Editar Item')


@bp.route('/<int:id>/acquire', methods=['POST'])
@login_required
def mark_acquired(id):
    """Marcar un item como adquirido"""
    item = WishlistItem.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    if item.acquired:
        flash('Este item ya fue marcado como adquirido', 'warning')
    else:
        item.acquired = True
        item.acquired_date = datetime.utcnow().date()
        db.session.commit()
        flash(f'"{item.title}" marcado como adquirido', 'success')

    return redirect(url_for('wishlist.detail', id=item.id))


@bp.route('/<int:id>/unacquire', methods=['POST'])
@login_required
def unmark_acquired(id):
    """Desmarcar un item como adquirido"""
    item = WishlistItem.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    if not item.acquired:
        flash('Este item no está marcado como adquirido', 'warning')
    else:
        item.acquired = False
        item.acquired_date = None
        db.session.commit()
        flash(f'"{item.title}" desmarcado como adquirido', 'success')

    return redirect(url_for('wishlist.detail', id=item.id))


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Eliminar un item de wishlist"""
    item = WishlistItem.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    title = item.title
    db.session.delete(item)
    db.session.commit()

    flash(f'"{title}" eliminado de tu lista de deseos', 'success')
    return redirect(url_for('wishlist.index'))
