from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Length
class F_Login(FlaskForm):
    txtUsuario = StringField("Usuario", validators=[DataRequired("Debe ingresar su usuario")])
    txtPassword = PasswordField("Contraseña", validators=[DataRequired("Debe ingresar su contraseña"), Length(
        min=8, max=-1, message="El mínimo de carácteres para la contraseña es de %(min)d")])
