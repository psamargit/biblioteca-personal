"""
Vistas de libros (CRUD, búsqueda, importación, exportación)
"""
import csv
import io
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import or_
from app import db
from app.models import Book, Tag, Owner
from app.forms import BookForm, SearchForm, ImportForm
from app.utils.helpers import save_cover_image, delete_cover_image, parse_csv_date, sanitize_isbn

bp = Blueprint('books', __name__, url_prefix='/books')


@bp.route('/')
@login_required
def index():
    """Lista de libros con paginación"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Obtener parámetros de filtro y búsqueda
    query = request.args.get('q', '')
    book_type = request.args.get('type', '')
    status = request.args.get('status', '')
    genre = request.args.get('genre', '')
    owner_id = request.args.get('owner_id', '', type=str)
    view_mode = request.args.get('view', 'table')  # table o cards

    # Construir query base
    books_query = Book.query.filter_by(user_id=current_user.id)

    # Aplicar filtros
    if query:
        search_filter = or_(
            Book.title.ilike(f'%{query}%'),
            Book.authors.ilike(f'%{query}%'),
            Book.isbn.ilike(f'%{query}%'),
            Book.description.ilike(f'%{query}%')
        )
        books_query = books_query.filter(search_filter)

    if book_type:
        books_query = books_query.filter_by(book_type=book_type)

    if status:
        books_query = books_query.filter_by(status=status)

    if genre:
        books_query = books_query.filter_by(genre=genre)

    if owner_id:
        books_query = books_query.filter_by(owner_id=int(owner_id))

    # Ordenar por fecha de creación descendente
    books_query = books_query.order_by(Book.created_at.desc())

    # Paginar
    pagination = books_query.paginate(page=page, per_page=per_page, error_out=False)
    books = pagination.items

    # Obtener géneros únicos para el filtro
    genres = db.session.query(Book.genre).filter(
        Book.user_id == current_user.id,
        Book.genre.isnot(None),
        Book.genre != ''
    ).distinct().order_by(Book.genre).all()
    genres = [g[0] for g in genres]

    # Obtener propietarios para el filtro
    owners = Owner.query.filter_by(user_id=current_user.id, is_active=True).order_by(Owner.name).all()

    return render_template('books/index.html',
                         books=books,
                         pagination=pagination,
                         genres=genres,
                         owners=owners,
                         view_mode=view_mode)


@bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    """Búsqueda avanzada de libros"""
    form = SearchForm()
    books = []

    # Poblar opciones de propietarios
    owners = Owner.query.filter_by(user_id=current_user.id, is_active=True).order_by(Owner.name).all()
    form.owner_id.choices = [('', 'Todos')] + [(str(o.id), o.name) for o in owners]

    if form.validate_on_submit():
        filters = {
            'genre': form.genre.data,
            'author': form.author.data,
            'book_type': form.book_type.data,
            'status': form.status.data,
            'owner_id': form.owner_id.data,
            'year_from': form.year_from.data,
            'year_to': form.year_to.data
        }

        # Usar el método de búsqueda del modelo
        books_query = Book.search(
            query=form.query.data,
            filters=filters,
            user_id=current_user.id
        )

        books = books_query.order_by(Book.created_at.desc()).all()

    return render_template('books/search.html', form=form, books=books)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Agregar un nuevo libro"""
    form = BookForm()

    # Poblar opciones de propietarios
    owners = Owner.query.filter_by(user_id=current_user.id, is_active=True).order_by(Owner.name).all()
    form.owner_id.choices = [('', 'Sin asignar')] + [(str(o.id), o.name) for o in owners]

    if form.validate_on_submit():
        # Crear libro
        book = Book(
            title=form.title.data,
            authors=form.authors.data,
            isbn=sanitize_isbn(form.isbn.data) if form.isbn.data else None,
            publisher=form.publisher.data,
            publication_year=form.publication_year.data,
            genre=form.genre.data,
            book_type=form.book_type.data,
            status=form.status.data,
            owner_id=form.owner_id.data,
            location=form.location.data,
            format=form.format.data,
            description=form.description.data,
            notes=form.notes.data,
            acquisition_date=form.acquisition_date.data,
            price=form.price.data,
            user_id=current_user.id
        )

        # Manejar imagen de portada
        if form.cover_file.data:
            cover_path = save_cover_image(form.cover_file.data)
            if cover_path:
                book.cover_image = cover_path
        elif form.cover_image.data:
            book.cover_image = form.cover_image.data

        # Procesar etiquetas
        if form.tags.data:
            tag_names = [t.strip() for t in form.tags.data.split(',') if t.strip()]
            for tag_name in tag_names:
                # Buscar o crear etiqueta
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                book.tags.append(tag)

        db.session.add(book)
        db.session.commit()

        flash(f'Libro "{book.title}" agregado exitosamente', 'success')
        return redirect(url_for('books.detail', id=book.id))

    return render_template('books/form.html', form=form, title='Agregar Libro')


@bp.route('/<int:id>')
@login_required
def detail(id):
    """Ver detalles de un libro"""
    book = Book.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('books/detail.html', book=book)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar un libro"""
    book = Book.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = BookForm(obj=book)

    # Poblar opciones de propietarios
    owners = Owner.query.filter_by(user_id=current_user.id, is_active=True).order_by(Owner.name).all()
    form.owner_id.choices = [('', 'Sin asignar')] + [(str(o.id), o.name) for o in owners]

    if form.validate_on_submit():
        # Actualizar campos
        book.title = form.title.data
        book.authors = form.authors.data
        book.isbn = sanitize_isbn(form.isbn.data) if form.isbn.data else None
        book.publisher = form.publisher.data
        book.publication_year = form.publication_year.data
        book.genre = form.genre.data
        book.book_type = form.book_type.data
        book.status = form.status.data
        book.owner_id = form.owner_id.data
        book.location = form.location.data
        book.format = form.format.data
        book.description = form.description.data
        book.notes = form.notes.data
        book.acquisition_date = form.acquisition_date.data
        book.price = form.price.data

        # Actualizar imagen de portada
        if form.cover_file.data:
            # Eliminar imagen anterior si existe
            if book.cover_image and not book.cover_image.startswith('http'):
                delete_cover_image(book.cover_image)

            cover_path = save_cover_image(form.cover_file.data)
            if cover_path:
                book.cover_image = cover_path
        elif form.cover_image.data:
            book.cover_image = form.cover_image.data

        # Actualizar etiquetas
        book.tags.clear()
        if form.tags.data:
            tag_names = [t.strip() for t in form.tags.data.split(',') if t.strip()]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                book.tags.append(tag)

        db.session.commit()

        flash(f'Libro "{book.title}" actualizado exitosamente', 'success')
        return redirect(url_for('books.detail', id=book.id))

    # Prellenar tags y owner en el formulario
    if request.method == 'GET':
        form.tags.data = ', '.join([tag.name for tag in book.tags])
        form.owner_id.data = str(book.owner_id) if book.owner_id else ''

    return render_template('books/form.html', form=form, title='Editar Libro', book=book)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Eliminar un libro"""
    book = Book.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    # Eliminar imagen de portada si existe
    if book.cover_image and not book.cover_image.startswith('http'):
        delete_cover_image(book.cover_image)

    title = book.title
    db.session.delete(book)
    db.session.commit()

    flash(f'Libro "{title}" eliminado exitosamente', 'success')
    return redirect(url_for('books.index'))


@bp.route('/export')
@login_required
def export():
    """Exportar inventario a CSV"""
    books = Book.query.filter_by(user_id=current_user.id).order_by(Book.title).all()

    # Crear archivo CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output)

    # Escribir encabezados
    writer.writerow([
        'Título', 'Autores', 'ISBN', 'Editorial', 'Año de Publicación',
        'Género', 'Tipo', 'Estado', 'Ubicación', 'Formato',
        'Descripción', 'Notas', 'Fecha de Adquisición', 'Precio', 'Etiquetas'
    ])

    # Escribir datos
    for book in books:
        writer.writerow([
            book.title,
            book.authors,
            book.isbn,
            book.publisher,
            book.publication_year,
            book.genre,
            book.book_type,
            book.status,
            book.location,
            book.format,
            book.description,
            book.notes,
            book.acquisition_date.isoformat() if book.acquisition_date else '',
            book.price,
            ', '.join([tag.name for tag in book.tags])
        ])

    # Preparar para descarga
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),  # UTF-8 con BOM para Excel
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'biblioteca_{current_user.username}.csv'
    )


@bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_books():
    """Importar libros desde CSV"""
    form = ImportForm()

    if form.validate_on_submit():
        file = form.csv_file.data
        stream = io.StringIO(file.stream.read().decode("utf-8-sig"), newline=None)
        csv_reader = csv.DictReader(stream)

        imported_count = 0
        errors = []

        for row_num, row in enumerate(csv_reader, start=2):
            try:
                # Validar campos requeridos
                if not row.get('Título') or not row.get('Autores'):
                    errors.append(f'Fila {row_num}: Título y Autores son requeridos')
                    continue

                # Crear libro
                book = Book(
                    title=row.get('Título', '').strip(),
                    authors=row.get('Autores', '').strip(),
                    isbn=sanitize_isbn(row.get('ISBN', '').strip()) if row.get('ISBN') else None,
                    publisher=row.get('Editorial', '').strip() or None,
                    publication_year=int(row.get('Año de Publicación', 0)) or None,
                    genre=row.get('Género', '').strip() or None,
                    book_type=row.get('Tipo', 'physical').strip(),
                    status=row.get('Estado', 'unread').strip(),
                    location=row.get('Ubicación', '').strip() or None,
                    format=row.get('Formato', '').strip() or None,
                    description=row.get('Descripción', '').strip() or None,
                    notes=row.get('Notas', '').strip() or None,
                    acquisition_date=parse_csv_date(row.get('Fecha de Adquisición', '')),
                    price=float(row.get('Precio', 0)) if row.get('Precio') else None,
                    user_id=current_user.id
                )

                # Procesar etiquetas
                if row.get('Etiquetas'):
                    tag_names = [t.strip() for t in row.get('Etiquetas', '').split(',') if t.strip()]
                    for tag_name in tag_names:
                        tag = Tag.query.filter_by(name=tag_name).first()
                        if not tag:
                            tag = Tag(name=tag_name)
                            db.session.add(tag)
                        book.tags.append(tag)

                db.session.add(book)
                imported_count += 1

            except Exception as e:
                errors.append(f'Fila {row_num}: {str(e)}')

        db.session.commit()

        if imported_count > 0:
            flash(f'{imported_count} libros importados exitosamente', 'success')

        if errors:
            flash(f'Se encontraron {len(errors)} errores. Revisa el log para más detalles.', 'warning')
            for error in errors[:10]:  # Mostrar solo los primeros 10 errores
                flash(error, 'danger')

        return redirect(url_for('books.index'))

    return render_template('books/import.html', form=form)


@bp.route('/scan')
@login_required
def scan():
    """Página de escaneo de códigos de barras"""
    return render_template('books/scan.html')


@bp.route('/api/barcode/<barcode>')
@login_required
def check_barcode(barcode):
    """API para verificar si un libro existe por código de barras"""
    book = Book.query.filter_by(
        isbn=sanitize_isbn(barcode),
        user_id=current_user.id
    ).first()

    if book:
        return jsonify({
            'found': True,
            'book': book.to_dict(),
            'url': url_for('books.detail', id=book.id)
        })

    return jsonify({'found': False})
