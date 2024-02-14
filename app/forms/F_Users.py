from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, PasswordField, SelectField, StringField
from wtforms.validators import DataRequired, Length, EqualTo
class F_Registro_Usuario(FlaskForm):
    txtPersonaCod = HiddenField('Persona', validators=[DataRequired("El campo de persona es requerido")])
    txtPassword = StringField('Contraseña')
    sltRol = SelectField('Apellidos', coerce=int)
    sltEstado = SelectField("Estado", choices=[('A', 'ACTIVO'), ('I', 'INACTIVO')])
    
class F_Cambio_Contrasena(FlaskForm):
    txtOldPassword = PasswordField("Contraseña Actual", validators=[DataRequired("El campo de contraseña actual es requerido")])
    txtNewPassword = PasswordField("Nueva Contraseña", validators=[DataRequired("El campo de contraseña nueva es requerido"), Length(min=8, message="La contraseña debe tener al menos 8 caracteres")])
    txtConfirmPassword = PasswordField("Confirmar Contraseña", validators=[DataRequired("El campo de contraseña nueva es requerido"), Length(min=8, message="La contraseña debe tener al menos 8 caracteres"), EqualTo("txtNewPassword", message="Las contraseñas no coinciden")])
