"""
Formularios de lista de deseos
"""
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange, URL


class WishlistItemForm(FlaskForm):
    """Formulario para agregar items a la lista de deseos"""

    title = StringField('Título *', validators=[
        DataRequired(message='El título es requerido'),
        Length(max=255, message='El título no puede exceder 255 caracteres')
    ])
    authors = StringField('Autor(es)', validators=[
        Optional(),
        Length(max=255, message='Los autores no pueden exceder 255 caracteres')
    ], description='Separar múltiples autores con comas')
    isbn = StringField('ISBN', validators=[
        Optional(),
        Length(max=20, message='El ISBN no puede exceder 20 caracteres')
    ])
    publisher = StringField('Editorial', validators=[
        Optional(),
        Length(max=150, message='La editorial no puede exceder 150 caracteres')
    ])
    estimated_price = FloatField('Precio Estimado', validators=[
        Optional(),
        NumberRange(min=0, message='El precio no puede ser negativo')
    ])
    priority = SelectField('Prioridad',
        choices=[('1', 'Alta'), ('2', 'Media'), ('3', 'Baja')],
        default='3',
        coerce=int
    )
    url = StringField('URL de Compra', validators=[
        Optional(),
        URL(message='Debe ser una URL válida'),
        Length(max=500, message='La URL no puede exceder 500 caracteres')
    ])
    notes = TextAreaField('Notas', validators=[Optional()])
    submit = SubmitField('Agregar a Lista de Deseos')
