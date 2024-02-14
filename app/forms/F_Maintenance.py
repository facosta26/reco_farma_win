
from flask_wtf import FlaskForm
from wtforms import DateField, HiddenField, IntegerField, PasswordField, SelectField, StringField, FileField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
class F_Especialidad_Medica(FlaskForm):
    txtDescripcionME = StringField("Descripción Especialidad Médica", validators=[DataRequired("El campo de Descripción Especialidad Médica es requerido")])
    sltEstadoME = SelectField("Estado", validators=[DataRequired("El campo de Estado es requerido")], choices=[("A", "ACTIVO"), ("I", "INACTIVO")])
    txtMEcod = HiddenField("Código de Especialidad Médica")
    
class F_Instituciones_Medicas(FlaskForm):
    txtItinIM = StringField("RUC", validators=[DataRequired("El RUC es un campo Requerido")])
    txtNombreFantasiaIM = StringField("Nombre Fantasía", validators=[DataRequired("El Nombre de Fantasia es un campo Requerido")])
    txtRazonSocialIM = StringField("Razon Social", validators=[DataRequired("El Razon Social es un campo Requerido")])
    sltEstadoIM = SelectField("Estado", validators=[DataRequired("El campo de Estado es requerido")], choices=[("A", "ACTIVO"), ("I", "INACTIVO")])
    txtIMcod = HiddenField("Código de Institución Médica")
    
class F_Tipos_Empaques(FlaskForm):
    txtDescripcionTE = StringField("Descripción Tipo de Empaque", validators=[DataRequired("El campo de Descripción Tipo de Empaque es requerido")])
    sltEstadoTE = SelectField("Estado", validators=[DataRequired("El campo de Estado es requerido")], choices=[("A", "ACTIVO"), ("I", "INACTIVO")])
    txtTEcod = HiddenField("Código de Tipo de Empaque")