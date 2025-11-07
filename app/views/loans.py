"""
Vistas de préstamos
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Loan, Book
from app.forms import LoanForm

bp = Blueprint('loans', __name__, url_prefix='/loans')


@bp.route('/')
@login_required
def index():
    """Lista de préstamos"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'active')  # active, returned, overdue

    # Construir query base
    loans_query = Loan.query.join(Book).filter(Book.user_id == current_user.id)

    # Aplicar filtros
    if status_filter == 'active':
        loans_query = loans_query.filter(Loan.returned == False)
    elif status_filter == 'returned':
        loans_query = loans_query.filter(Loan.returned == True)
    elif status_filter == 'overdue':
        loans_query = loans_query.filter(
            Loan.returned == False,
            Loan.due_date < db.func.current_date()
        )

    # Ordenar por fecha de préstamo descendente
    loans_query = loans_query.order_by(Loan.loan_date.desc())

    # Paginar
    pagination = loans_query.paginate(page=page, per_page=20, error_out=False)
    loans = pagination.items

    return render_template('loans/index.html',
                         loans=loans,
                         pagination=pagination,
                         status_filter=status_filter)


@bp.route('/add/<int:book_id>', methods=['GET', 'POST'])
@login_required
def add(book_id):
    """Registrar un nuevo préstamo"""
    book = Book.query.filter_by(id=book_id, user_id=current_user.id).first_or_404()

    # Verificar que el libro esté disponible
    if not book.is_available:
        flash(f'El libro "{book.title}" ya está prestado', 'warning')
        return redirect(url_for('books.detail', id=book.id))

    form = LoanForm()

    if form.validate_on_submit():
        # Crear préstamo
        loan = Loan(
            book_id=book.id,
            user_id=current_user.id,
            borrower_name=form.borrower_name.data,
            borrower_email=form.borrower_email.data,
            borrower_phone=form.borrower_phone.data,
            loan_date=form.loan_date.data,
            due_date=form.due_date.data,
            notes=form.notes.data
        )

        db.session.add(loan)
        db.session.commit()

        flash(f'Préstamo de "{book.title}" registrado exitosamente', 'success')
        return redirect(url_for('loans.detail', id=loan.id))

    return render_template('loans/form.html', form=form, book=book, title='Registrar Préstamo')


@bp.route('/<int:id>')
@login_required
def detail(id):
    """Ver detalles de un préstamo"""
    loan = Loan.query.join(Book).filter(
        Loan.id == id,
        Book.user_id == current_user.id
    ).first_or_404()

    return render_template('loans/detail.html', loan=loan)


@bp.route('/<int:id>/return', methods=['POST'])
@login_required
def mark_returned(id):
    """Marcar un préstamo como devuelto"""
    loan = Loan.query.join(Book).filter(
        Loan.id == id,
        Book.user_id == current_user.id
    ).first_or_404()

    if loan.returned:
        flash('Este préstamo ya fue marcado como devuelto', 'warning')
    else:
        loan.mark_as_returned()
        flash(f'Préstamo de "{loan.book.title}" marcado como devuelto', 'success')

    return redirect(url_for('loans.detail', id=loan.id))


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar un préstamo"""
    loan = Loan.query.join(Book).filter(
        Loan.id == id,
        Book.user_id == current_user.id
    ).first_or_404()

    form = LoanForm(obj=loan)

    if form.validate_on_submit():
        loan.borrower_name = form.borrower_name.data
        loan.borrower_email = form.borrower_email.data
        loan.borrower_phone = form.borrower_phone.data
        loan.loan_date = form.loan_date.data
        loan.due_date = form.due_date.data
        loan.notes = form.notes.data

        db.session.commit()

        flash(f'Préstamo actualizado exitosamente', 'success')
        return redirect(url_for('loans.detail', id=loan.id))

    return render_template('loans/form.html', form=form, loan=loan, title='Editar Préstamo')


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Eliminar un préstamo"""
    loan = Loan.query.join(Book).filter(
        Loan.id == id,
        Book.user_id == current_user.id
    ).first_or_404()

    db.session.delete(loan)
    db.session.commit()

    flash('Préstamo eliminado exitosamente', 'success')
    return redirect(url_for('loans.index'))
