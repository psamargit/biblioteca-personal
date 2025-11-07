"""
Formularios de autenticación
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    """Formulario de inicio de sesión"""

    username = StringField('Usuario', validators=[
        DataRequired(message='El usuario es requerido'),
        Length(min=3, max=80, message='El usuario debe tener entre 3 y 80 caracteres')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es requerida')
    ])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')


class RegistrationForm(FlaskForm):
    """Formulario de registro de usuario"""

    username = StringField('Usuario', validators=[
        DataRequired(message='El usuario es requerido'),
        Length(min=3, max=80, message='El usuario debe tener entre 3 y 80 caracteres')
    ])
    email = StringField('Correo Electrónico', validators=[
        DataRequired(message='El correo electrónico es requerido'),
        Email(message='Correo electrónico inválido')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es requerida'),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    password2 = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(message='Debes confirmar la contraseña'),
        EqualTo('password', message='Las contraseñas no coinciden')
    ])
    submit = SubmitField('Registrarse')

    def validate_username(self, username):
        """Valida que el usuario no exista"""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('El nombre de usuario ya está en uso. Por favor elige otro.')

    def validate_email(self, email):
        """Valida que el email no exista"""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('El correo electrónico ya está registrado.')
