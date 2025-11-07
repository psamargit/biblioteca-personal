"""
Formularios de propietarios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Email


class OwnerForm(FlaskForm):
    """Formulario para crear/editar propietarios"""

    name = StringField('Nombre *', validators=[
        DataRequired(message='El nombre es requerido'),
        Length(max=100, message='El nombre no puede exceder 100 caracteres')
    ])

    relationship = StringField('Parentesco', validators=[
        Optional(),
        Length(max=50, message='El parentesco no puede exceder 50 caracteres')
    ], description='Ej: Padre, Madre, Hijo/a, Hermano/a, etc.')

    email = StringField('Correo Electrónico', validators=[
        Optional(),
        Email(message='Correo electrónico inválido'),
        Length(max=120, message='El correo no puede exceder 120 caracteres')
    ])

    color = StringField('Color de Identificación', validators=[
        Optional(),
        Length(max=7, message='El color debe ser un código hexadecimal (#RRGGBB)')
    ], default='#007bff', description='Color para identificar visualmente al propietario')

    notes = TextAreaField('Notas', validators=[Optional()])

    is_active = BooleanField('Activo', default=True)

    submit = SubmitField('Guardar')
