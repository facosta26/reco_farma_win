from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, HiddenField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, NumberRange
class F_Doctores(FlaskForm):
    
    txtPersonaCod = HiddenField("Persona", validators=[DataRequired("El campo de Persona es requerido")])
    txtDoctorMatricula = IntegerField("Matrícula Profesional", validators=[DataRequired(
        "El campo de Matrícula Profesional es requerido"), NumberRange(min=0)])
    sltEspecialidadMedica = SelectField("Especialidad Médica", validators=[DataRequired(
        "El campo de Especialidad Médica es requerido")], coerce=int, default='2')
    sltInstitucionMedica = SelectField("Institución Médica", validators=[DataRequired("El campo de Institución Médica es requerido")], coerce=int, default="1")
    sltEstado = SelectField("Estado", choices=[('A', 'ACTIVO'), ('I', 'INACTIVO')])


class MedicinaIndicaciones(FlaskForm):
    txtMedicina = StringField('Medicina', validators=[DataRequired("El campo de Médicina es requerido")])
    txtIndicacionesMedicas = TextAreaField('Indicaciones Médicas', validators=[DataRequired("El campo de Médicina es requerido")])

class F_Consulta_Medica(FlaskForm):
    dynamic_fields = FieldList(FormField(MedicinaIndicaciones), min_entries=1)
    add_field = SubmitField('Add Dynamic Field')
    txtPersonaCod = HiddenField("Persona", validators=[DataRequired("El campo de Persona es requerido")])
    txtDiagnostico = TextAreaField("Diagnóstico", validators=[DataRequired("El campo de Diagnostico es requerido")])
    submit = SubmitField('Submit')
    
    def get_field_data(self):
        data = self.data
        data['dynamic_fields'] = [
            field.data for field in self.dynamic_fields
        ]
        return data
