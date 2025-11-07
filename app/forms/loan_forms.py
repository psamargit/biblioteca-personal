"""
Formularios de préstamos
"""
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Email, Length, ValidationError
from datetime import datetime, timedelta


class LoanForm(FlaskForm):
    """Formulario para registrar préstamos"""

    borrower_name = StringField('Nombre del Prestatario *', validators=[
        DataRequired(message='El nombre es requerido'),
        Length(max=150, message='El nombre no puede exceder 150 caracteres')
    ])
    borrower_email = StringField('Correo Electrónico', validators=[
        Optional(),
        Email(message='Correo electrónico inválido'),
        Length(max=120, message='El correo no puede exceder 120 caracteres')
    ])
    borrower_phone = StringField('Teléfono', validators=[
        Optional(),
        Length(max=20, message='El teléfono no puede exceder 20 caracteres')
    ])
    loan_date = DateField('Fecha de Préstamo *',
        format='%Y-%m-%d',
        default=datetime.utcnow().date,
        validators=[DataRequired(message='La fecha de préstamo es requerida')]
    )
    due_date = DateField('Fecha de Devolución *',
        format='%Y-%m-%d',
        default=lambda: datetime.utcnow().date() + timedelta(days=30),
        validators=[DataRequired(message='La fecha de devolución es requerida')]
    )
    notes = TextAreaField('Notas', validators=[Optional()])
    submit = SubmitField('Registrar Préstamo')

    def validate_due_date(self, due_date):
        """Valida que la fecha de devolución sea posterior a la fecha de préstamo"""
        if due_date.data and self.loan_date.data and due_date.data < self.loan_date.data:
            raise ValidationError('La fecha de devolución debe ser posterior a la fecha de préstamo')
