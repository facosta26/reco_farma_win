from datetime import date, datetime
from flask import Blueprint, render_template, json, render_template_string, request, session
from app.forms.F_Doctors import F_Consulta_Medica, F_Doctores
from app.forms.F_People import F_Busqueda_Persona
from app.models.Models import People, PeoplePhotos, PeoplePrescription, PeoplePrescriptionDetails, db, Doctors, Institutions, MedicalEspecialties
from sqlalchemy import or_, func
from app.utils.utils import asuncion_timezone, check_role
from sqlalchemy.orm import aliased

class C_Doctors():
    doctors = Blueprint('doctors', __name__)

    @doctors.route('/doctors_register')
    @check_role(['ADMINISTRADOR'])
    def doctors_register():
        formBusq = F_Busqueda_Persona()
        formDoct = F_Doctores()
        me = [(ep.mees_id, ep.mees_desc) for ep in MedicalEspecialties.query.all()]
        formDoct.sltEspecialidadMedica.choices=me
        inst = [(i.inst_id, i.inst_trade_name) for i in Institutions.query.all()]
        formDoct.sltInstitucionMedica.choices = inst
        return render_template('v_doctors_register.html', title="Registro de Médicos", formBusq=formBusq, formDoct=formDoct)

    @doctors.route('/doctors_data_register', methods=['POST'])
    @check_role(['ADMINISTRADOR'])
    def doctors_data_register():
        message = {"correcto": '', "alerta": '', "error": ''}
        form = F_Doctores()
        me = [(ep.mees_id, ep.mees_desc) for ep in MedicalEspecialties.query.filter_by(mees_state='A').all()]
        form.sltEspecialidadMedica.choices=me
        inst = [(i.inst_id, i.inst_trade_name) for i in Institutions.query.filter_by(inst_state='A').all()]
        form.sltInstitucionMedica.choices = inst
        if form.validate_on_submit():
            person = form.txtPersonaCod.data
            profesional_registration = form.txtDoctorMatricula.data
            especialty = form.sltEspecialidadMedica.data
            institution = form.sltInstitucionMedica.data
            state = form.sltEstado.data
            doctors = Doctors.query.filter(or_(Doctors.doct_peop_id == person, Doctors.doct_professional_registration == profesional_registration)).first()
            if doctors is not None:
                doctors.doct_peop_id = person
                doctors.doct_professional_registration = profesional_registration
                doctors.doct_mees_id = especialty
                doctors.doct_inst_id = institution
                doctors.doct_state = state
                doctors.doct_user_updated_id = session['user_id']
                db.session.commit()
                message['correcto'] = '<strong>Se ha realizado correctamente el registro de los datos del médico existente </strong>'
            else:
                doctor = Doctors()
                doctor.doct_peop_id = person
                doctor.doct_professional_registration = profesional_registration
                doctor.doct_mees_id = especialty
                doctor.doct_inst_id = institution
                doctor.doct_state = state
                doctor.doct_user_created_id = session['user_id']
                db.session.add(doctor)
                db.session.commit()
                message['correcto'] = '<strong>Se ha realizado correctamente el registro de los datos del médico </strong>'
        else:
            errores = {}
            for campo, errores_campo in form.errors.items():
                label = form[campo].label.text
                errores[campo] = '{}: {} <br>'.format(
                    label, ', '.join(errores_campo))
            message['error'] = {}
            message['error']['validacion'] = '<strong>Por favor, corrija los errores en el formulario.</strong><br>'
            message['error']['detalles'] = errores
           
        return json.dumps(message)
    
    @doctors.route('/get_doctors_list', methods=['GET'])
    @check_role(['ADMINISTRADOR', 'MEDICO'])
    def get_doctors_list():
        message = {"correcto": '', "alerta": '', "error": ''}
        doctors = Doctors.query.with_entities(Doctors.doct_id.label("id"), (People.peop_names+' '+People.peop_lastnames).label('person'), Doctors.doct_peop_id.label('person_id'), Institutions.inst_trade_name.label('institute'), Institutions.inst_id.label('institute_id'), MedicalEspecialties.mees_desc.label('especialty'), MedicalEspecialties.mees_id.label('especialty_id'), Doctors.doct_state.label('state'), Doctors.doct_professional_registration.label('prof_reg')).join(People).join(Institutions).join(MedicalEspecialties).paginate(
            page=request.args.get('page', 1), per_page=10)
        return {
            'data': 
            [
                {
                    "id": doctor.id,
                    "person": doctor.person,
                    "person_id": doctor.person_id,
                    "state": doctor.state,
                    "state_full": "ACTIVO" if doctor.state == "A" else "INACTIVO",
                    "institute": doctor.institute,
                    "institute_id": doctor.institute_id,
                    "especialty": doctor.especialty,
                    "especialty_id": doctor.especialty_id,
                    "prof_reg": doctor.prof_reg,
                } for doctor in doctors
            ] ,
            'total': doctors.total
        }
        
    @doctors.route('/medical_consultations')
    @check_role(['MEDICO'])
    def medical_consultations():
        formConsulta = F_Consulta_Medica()
        formBusq = F_Busqueda_Persona()
        return render_template('v_medical_consultations.html', title="Consultas Médicas", formFP=formConsulta, formBusq=formBusq)

    @doctors.route('/registers_data_consultation', methods=['POST'])
    @check_role(['MEDICO'])
    def registers_data_consultation():
        message = {"correcto": '', "alerta": '', "error": ''}
        form = F_Consulta_Medica(request.form)
        if form.validate_on_submit():
            person = form.txtPersonaCod.data
            diagnostic = form.txtDiagnostico.data
            pepr_id = 0
            try:
                existConsult = PeoplePrescription.query.filter(PeoplePrescription.pepr_peop_id == person, PeoplePrescription.pepr_doct_id == session['user_id'], func.date(PeoplePrescription.pepr_created_at) == datetime.now(asuncion_timezone).strftime("%Y-%m-%d")).first()
                print(existConsult)
                if existConsult is not None:
                    pepr_id = existConsult.pepr_id
                    existConsult = PeoplePrescription()
                    existConsult.pepr_peop_id = person
                    existConsult.pepr_dx = diagnostic.upper()
                    existConsult.pepr_doct_id = session['user_id']
                    existConsult.pepr_state = 'A'
                    existConsult.pepr_user_updated_id = session['user_id']
                    db.session.commit()
                else:
                    consultation = PeoplePrescription()
                    consultation.pepr_peop_id = person
                    consultation.pepr_dx = diagnostic.upper()
                    consultation.pepr_doct_id = session['user_id']
                    consultation.pepr_state = 'A'
                    consultation.pepr_user_created_id = session['user_id']
                    db.session.add(consultation)
                    db.session.commit()
                    pepr_id = consultation.pepr_id
                for e in form.dynamic_fields.data:
                    existMedication = PeoplePrescriptionDetails.query.filter(PeoplePrescriptionDetails.prde_pepr_id == pepr_id, PeoplePrescriptionDetails.prde_medical_indications == e['txtIndicacionesMedicas'].upper(
                    ), PeoplePrescriptionDetails.prde_medicine == e['txtMedicina'].upper()).first()

                    if existMedication is not None:
                        existMedication = PeoplePrescriptionDetails()
                        existMedication.prde_pepr_id = pepr_id
                        existMedication.prde_medical_indications = e['txtIndicacionesMedicas'].upper()
                        existMedication.prde_medicine = e['txtMedicina'].upper()
                        existMedication.prde_state = 'A'
                        existMedication.prde_user_updated_id = session['user_id']
                        db.session.commit()
                        message['correcto'] = "Se ha registrado modificado los datos de la consulta"
                        message['consulting'] = pepr_id
                    else:
                        medication = PeoplePrescriptionDetails()
                        medication.prde_pepr_id = pepr_id
                        medication.prde_medical_indications = e['txtIndicacionesMedicas'].upper()
                        medication.prde_medicine = e['txtMedicina'].upper()
                        medication.prde_state = 'A'
                        medication.prde_user_created_id = session['user_id']
                        db.session.add(medication)
                        db.session.commit()
                        message['correcto'] = "Se ha registrado modificado los datos de la consulta"
                        message['consulting'] = pepr_id
            except Exception as e:
                db.session.rollback()
                raise e
            
        else:
            errores = {}
            for campo, errores_campo in form.errors.items():
                label = form[campo].label.text
                errores[campo] = '{}: {} <br>'.format(
                    label, ', '.join(errores_campo))
            message['error'] = {}
            message['error']['validacion'] = '<strong>Por favor, corrija los errores en el formulario.</strong><br>'
            message['error']['detalles'] = errores

        return json.dumps(message)
    
    @doctors.route('/get_dynamic_fields/<int:index>')
    @check_role(['MEDICO'])
    def get_dynamic_fields(index):
        template = '''
        <div class="col-md-6 mb-3">
            <div class="form-floating">
                <input type="text" class="form-control" name="dynamic_fields-{{ index }}-txtMedicina" placeholder="">
                <label>Medicamento {{ index+1 }}</label>
            </div>
        </div>
        <div class="col-md-6 mb-3">
            <div class="form-floating">
                <textarea class="form-control" name="dynamic_fields-{{ index }}-txtIndicacionesMedicas" placeholder="" style="height: 100px"></textarea>
                <label>Instrucciones Médicas del Medicamento {{ index+1 }}</label>
            </div>
        </div>
        '''

        # Renderizar el string de plantilla y enviarlo como respuesta
        return render_template_string(template, index=index)
    
    @doctors.route('/consultation_details/<consultation>')
    @check_role(['MEDICO'])
    def consultation_details(consultation):
        patient_alias = aliased(People, name='patient_alias')
        doctor_alias = aliased(People, name='doctor_alias')

        consultation = db.session.query(
            PeoplePrescription.pepr_id.label('consultation'),
            patient_alias.peop_id.label('patient_id'),
            PeoplePrescription.pepr_dx.label('diagnostic'),
            (patient_alias.peop_names+ ' ' + patient_alias.peop_lastnames).label('patient'),
            patient_alias.peop_dni.label('dni'),
            patient_alias.peop_gender.label('gender'),
            patient_alias.peop_birthdate.label('birthdate'),
            doctor_alias.peop_id.label('doctor_id'),
            PeoplePrescription.pepr_dx.label('diagnostic'),
            (doctor_alias.peop_names+ ' ' + doctor_alias.peop_lastnames).label('doctor')
        ).join(patient_alias, PeoplePrescription.pepr_peop_id == patient_alias.peop_id).join(doctor_alias, PeoplePrescription.pepr_doct_id == doctor_alias.peop_id).filter(PeoplePrescription.pepr_id==consultation).first()
        photo = PeoplePhotos.query.filter(PeoplePhotos.peph_peop_id==consultation.patient_id).order_by(PeoplePhotos.peph_id.desc()).first()
        medications = PeoplePrescriptionDetails.query.filter(PeoplePrescriptionDetails.prde_pepr_id==consultation.consultation).all()
        return render_template('v_consultation_details.html', title='Detalles de Consulta', consultations=consultation, photo=photo, medications=medications)