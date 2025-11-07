"""
Formularios de etiquetas
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class TagForm(FlaskForm):
    """Formulario para crear/editar etiquetas"""

    name = StringField('Nombre *', validators=[
        DataRequired(message='El nombre es requerido'),
        Length(max=50, message='El nombre no puede exceder 50 caracteres')
    ])
    color = StringField('Color', validators=[
        Optional(),
        Length(max=7, message='El color debe ser un código hexadecimal (#RRGGBB)')
    ], default='#007bff', description='Código hexadecimal (ej: #007bff)')
    description = StringField('Descripción', validators=[
        Optional(),
        Length(max=200, message='La descripción no puede exceder 200 caracteres')
    ])
    submit = SubmitField('Guardar')
