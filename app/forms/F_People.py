from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, PasswordField, SelectField, StringField, FileField
from wtforms.validators import DataRequired, Length, Optional, NumberRange


from wtforms import ValidationError


def al_menos_un_campo_lleno(form):
    for field in form.fields:
        if field.data:
            return True
    raise ValidationError("Al menos un campo debe estar lleno.")


class F_Busqueda_Persona(FlaskForm):
    txtCedulaBusqPersona = IntegerField('Cédula', validators=[NumberRange(min=0),Optional()])
    txtNombBusqPersona = StringField('Nombres')
    txtApellidosBusqPersona = StringField('Apellidos')

class F_Persona(FlaskForm):
    txtDniPersona = IntegerField("Cédula", validators=[DataRequired(
        "La cédula es un campo Requerido"), NumberRange(min=0)])
    txtNombrePersona = StringField(
        "Nombres", validators=[DataRequired("El nombre es un campo Requerido")])
    txtApellidoPersona = StringField("Apellidos", validators=[
                                     DataRequired("El apellido es un campo Requerido")])
    sltSexoPersona = SelectField("Sexo", validators=[DataRequired("El sexo es un campo requerido")], choices=[("F", "FEMENINO"),("M", "MASCULINO")])
    txtFechaNacimiento = DateField("Fecha de Nacimiento", validators=[DataRequired("La fecha de nacimiento es un campo requerido")])

class F_Fotos_Persona(FlaskForm):
    capturedImage = FileField('Foto de Persona')
