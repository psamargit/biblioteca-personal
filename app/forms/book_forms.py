"""
Formularios relacionados con libros
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, IntegerField, FloatField, DateField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Optional, Length, NumberRange, URL
from datetime import datetime


class BookForm(FlaskForm):
    """Formulario para crear/editar libros"""

    # Información básica
    title = StringField('Título *', validators=[
        DataRequired(message='El título es requerido'),
        Length(max=255, message='El título no puede exceder 255 caracteres')
    ])
    authors = StringField('Autor(es) *', validators=[
        DataRequired(message='El autor es requerido'),
        Length(max=255, message='Los autores no pueden exceder 255 caracteres')
    ], description='Separar múltiples autores con comas')
    isbn = StringField('ISBN/Código de Barras', validators=[
        Optional(),
        Length(max=20, message='El ISBN no puede exceder 20 caracteres')
    ])
    publisher = StringField('Editorial', validators=[
        Optional(),
        Length(max=150, message='La editorial no puede exceder 150 caracteres')
    ])
    publication_year = IntegerField('Año de Publicación', validators=[
        Optional(),
        NumberRange(min=1000, max=datetime.now().year + 1,
                   message=f'El año debe estar entre 1000 y {datetime.now().year + 1}')
    ])

    # Categorización
    genre = StringField('Género/Categoría', validators=[
        Optional(),
        Length(max=100, message='El género no puede exceder 100 caracteres')
    ])
    book_type = SelectField('Tipo *',
        choices=[('physical', 'Físico'), ('digital', 'Digital')],
        validators=[DataRequired(message='El tipo es requerido')]
    )

    # Estado y ubicación
    status = SelectField('Estado de Lectura *',
        choices=[('unread', 'No leído'), ('reading', 'Leyendo'), ('read', 'Leído')],
        validators=[DataRequired(message='El estado es requerido')]
    )
    location = StringField('Ubicación', validators=[
        Optional(),
        Length(max=150, message='La ubicación no puede exceder 150 caracteres')
    ], description='Para físicos: estante, caja, etc.')
    format = StringField('Formato', validators=[
        Optional(),
        Length(max=50, message='El formato no puede exceder 50 caracteres')
    ], description='Para digitales: PDF, EPUB, MOBI, etc.')

    # Información adicional
    cover_image = StringField('URL de Portada', validators=[
        Optional(),
        URL(message='Debe ser una URL válida'),
        Length(max=255, message='La URL no puede exceder 255 caracteres')
    ])
    cover_file = FileField('O subir imagen de portada', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'],
                   'Solo se permiten imágenes (jpg, jpeg, png, gif, webp)')
    ])
    description = TextAreaField('Descripción', validators=[Optional()])
    notes = TextAreaField('Notas Personales', validators=[Optional()])
    acquisition_date = DateField('Fecha de Adquisición',
        format='%Y-%m-%d',
        validators=[Optional()]
    )
    price = FloatField('Precio', validators=[
        Optional(),
        NumberRange(min=0, message='El precio no puede ser negativo')
    ])

    # Tags (se manejará con JavaScript en el frontend)
    tags = StringField('Etiquetas', validators=[Optional()],
                      description='Separar etiquetas con comas')

    submit = SubmitField('Guardar')


class SearchForm(FlaskForm):
    """Formulario de búsqueda avanzada"""

    query = StringField('Buscar', validators=[Optional()])
    genre = StringField('Género', validators=[Optional()])
    author = StringField('Autor', validators=[Optional()])
    book_type = SelectField('Tipo',
        choices=[('', 'Todos'), ('physical', 'Físico'), ('digital', 'Digital')],
        validators=[Optional()]
    )
    status = SelectField('Estado',
        choices=[('', 'Todos'), ('unread', 'No leído'), ('reading', 'Leyendo'), ('read', 'Leído')],
        validators=[Optional()]
    )
    year_from = IntegerField('Año desde', validators=[
        Optional(),
        NumberRange(min=1000, max=datetime.now().year + 1)
    ])
    year_to = IntegerField('Año hasta', validators=[
        Optional(),
        NumberRange(min=1000, max=datetime.now().year + 1)
    ])
    submit = SubmitField('Buscar')


class ImportForm(FlaskForm):
    """Formulario para importar libros desde CSV"""

    csv_file = FileField('Archivo CSV *', validators=[
        DataRequired(message='Debes seleccionar un archivo CSV'),
        FileAllowed(['csv'], 'Solo se permiten archivos CSV')
    ])
    submit = SubmitField('Importar')
