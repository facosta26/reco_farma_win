from datetime import date, datetime
import os
import uuid
from flask import Blueprint, current_app, json, render_template, request, session
from sqlalchemy import func
from app.forms.F_People import F_Busqueda_Persona, F_Fotos_Persona, F_Persona
from app.models.Models import Doctors, People, PeoplePhotos, PeoplePrescription, PeoplePrescriptionDetails, db
from app.utils.utils import check_role
from sqlalchemy.orm import aliased

class C_People():
    peop = Blueprint('people', __name__)

    @peop.route('/search_people', methods=['POST'])
    @check_role(['ADMINISTRADOR', 'MEDICO', 'FARMACEUTICO'])
    def search_people():
        message = {"correcto": '', "alerta": '', "error": ''}
        form = F_Busqueda_Persona(request.form)
        if form.validate_on_submit():
            dni = form.txtCedulaBusqPersona.data
            names = form.txtNombBusqPersona.data
            lastnames = form.txtApellidosBusqPersona.data
            if dni:
                people = People.query.filter(People.peop_dni == dni).all()
            else:
                people = People.query.filter((People.peop_names + ' ' + People.peop_lastnames).like(
                    '%'+names.upper()+' '+lastnames.upper()+'%')).all()

            people_data = [
                {
                    "id": person.peop_id,
                    "dni": person.peop_dni,
                    "names": person.peop_names,
                    "lastname": person.peop_lastnames,
                    "birthdate": person.peop_birthdate.strftime("%d/%m/%Y"),
                    "gender": "MASCULINO" if person.peop_gender == 'M' else 'FEMENINO',
                    "age": C_People.calcular_edad(person.peop_birthdate)
                }
                for person in people
            ]
            message['correcto'] = people_data
            
            
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

    @peop.route('/people')
    @check_role(['ADMINISTRADOR', 'MEDICO', 'FARMACEUTICO'])
    def people():
        form = F_Persona()
        return render_template('v_people.html', title='Listado de Personas', form=form)

    @peop.route('/comprobate_dni', methods=['POST'])
    @check_role(['ADMINISTRADOR', 'MEDICO', 'FARMACEUTICO'])
    def comprobate_dni():
        message = {"correcto": '', "alerta": '', "error": ''}
        dni = request.form["txtDniPersona"]
        if not dni.isdigit() and dni != "":
            message["error"] = 'El DNI debe ser númerico.'
        else:
            if dni != "":
                person = People.query.filter_by(peop_dni=dni).first()
                if person is not None:
                    message['error'] = "Ya existe registrada una persona con el DNI ingresado"
                else:
                    message['correcto'] = "DNI valido"
        return json.dumps(message)

    @peop.route('/register_data', methods=['POST'])
    @check_role(['ADMINISTRADOR', 'MEDICO', 'FARMACEUTICO'])
    def register_data():
        message = {"correcto": '', "alerta": '', "error": ''}
        form = F_Persona(request.form)
        if form.validate_on_submit:
            dni = form.txtDniPersona.data
            names = form.txtNombrePersona.data
            lastnames = form.txtApellidoPersona.data
            gender = form.sltSexoPersona.data
            birthdate = form.txtFechaNacimiento.data
            exist_person = People.query.filter_by(peop_dni=dni).first()
            if exist_person is None:
                new_person = People(
                    peop_dni=dni,
                    peop_names=names.upper(),
                    peop_lastnames=lastnames.upper(),
                    peop_gender=gender,
                    peop_birthdate=birthdate,
                    peop_user_created_id=session["user_id"])
                db.session.add(new_person)
                db.session.commit()
                message['correcto'] = 'Se ha registrado correctamente a la persona'
                message['id'] = dni
            else:
                exist_person.peop_dni = dni
                exist_person.peop_names = names.upper()
                exist_person.peop_lastnames = lastnames.upper()
                exist_person.peop_gender = gender
                exist_person.peop_birthdate = birthdate
                exist_person.peop_user_updated_id = session["user_id"]
                db.session.commit()
                message['correcto'] = 'Se ha modificado correctamente a la persona'
                message['id'] = dni
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

    @peop.route('/get_people_data')
    @check_role(['ADMINISTRADOR', 'MEDICO', 'FARMACEUTICO'])
    def get_people_data():
        message = {"correcto": '', "alerta": '', "error": ''}
        people = People.query.with_entities(
            People.peop_id.label('id'),
            People.peop_names.label('names'),
            People.peop_lastnames.label('lastnames'),
            People.peop_dni.label('dni'),
            People.peop_gender.label('gender'),
            People.peop_birthdate.label('birthdate')).paginate(
            page=request.args.get('page', 1), per_page=10)
        return {
            "data": [
                {
                    "id": person.id,
                    "person": person.names+' '+person.lastnames,
                    "names": person.names,
                    "lastnames": person.lastnames,
                    "dni": person.dni,
                    "gender_desc": "MASCULINO" if person.gender == 'M' else 'FEMENINO',
                    "gender": person.gender,
                    "birthdate": person.birthdate.strftime("%Y-%m-%d"),
                    "age": C_People.calcular_edad(person.birthdate)
                } for person in people
            ],
            'total': people.total
        }

    @peop.route('/take_photo/<dni>')
    @check_role(['ADMINISTRADOR', 'MEDICO', 'FARMACEUTICO'])
    def take_photo(dni):
        form = F_Fotos_Persona()
        person_data = People.query.with_entities(People.peop_dni.label('dni'), People.peop_names.label(
            'names'), People.peop_lastnames.label('lastnames'), People.peop_birthdate.label('age'), People.peop_gender.label("gender")).filter_by(peop_dni=dni).first()
        return render_template('v_take_photo.html', title='Tomar Foto Persona', person_data=person_data, form=form, dni=dni)

    @peop.route('/register_person_photo/<dni>', methods=['POST'])
    @check_role(['ADMINISTRADOR', 'MEDICO', 'FARMACEUTICO'])
    def register_person_photo(dni):
        message = {"correcto": '', "alerta": '', "error": ''}
        form = F_Fotos_Persona(request.form)
        if form.validate_on_submit():
            if 'capturedImage' in request.files:
                image = request.files['capturedImage']
                if image:
                    filename = f'{uuid.uuid4()}.jpg'
                    # Ruta de la carpeta que deseas crear
                    carpeta_nueva = os.path.join(current_app.config['UPLOAD_FOLDER'], str(
                        'people_photo/')+dni)

                    # Verificar si la carpeta ya existe
                    if not os.path.exists(carpeta_nueva):
                        # Si no existe, crear la carpeta
                        os.makedirs(carpeta_nueva)
                    filepath = os.path.join(carpeta_nueva, filename)
                    image.save(filepath)
                    person = People.query.filter_by(peop_dni = dni).first()
                    new_photo = PeoplePhotos(
                        peph_path = dni+'/'+filename,
                        peph_peop_id = person.peop_id,
                        peph_user_created_id = session['user_id']
                    )
                    db.session.add(new_photo)
                    db.session.commit()
                    message['correcto'] = 'Se ha registrado correctamente '+filename
            else:
                message['error'] = 'Error al recibir la imagen'
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
    
    @peop.route('/get_person_last_photo/<person>')
    @check_role(['ADMINISTRADOR', 'MEDICO', 'FARMACEUTICO'])
    def get_person_last_photo(person):
        message = {"correcto": '', "alerta": '', "error": ''}
        photo = PeoplePhotos.query.filter_by(peph_peop_id=person).order_by(PeoplePhotos.peph_id.desc()).first()
        consultation = PeoplePrescription.query.with_entities(PeoplePrescription.pepr_id.label('id'), (People.peop_names+' '+People.peop_lastnames).label('doctor'), PeoplePrescription.pepr_created_at.label('date')).join(Doctors, Doctors.doct_id == PeoplePrescription.pepr_doct_id).join(People, People.peop_id == Doctors.doct_peop_id).filter(PeoplePrescription.pepr_peop_id == person).order_by(PeoplePrescription.pepr_id.desc()).paginate(
            page=1, per_page=10)
        message['photo'] = photo.peph_path if photo is not None else None
        message['consultation'] = [
            {
                "id": prescription.id,
                "doctor": prescription.doctor,
                "date": prescription.date.strftime("%d/%m/%Y")
                } for prescription in consultation
            ]
        return json.dumps(message)
    
    @peop.route('/get_person_prescription/<people>')
    def get_person_prescription(people):
        message = {"correcto": '', "alerta": '', "error": ''}
        patient_alias = aliased(People, name='patient_alias')
        doctor_alias = aliased(People, name='doctor_alias')
        consultation = db.session.query(
            PeoplePrescription.pepr_id.label('consultation'),
            patient_alias.peop_id.label('patient_id'),
            PeoplePrescription.pepr_dx.label('diagnostic'),
            (patient_alias.peop_names + ' ' +
             patient_alias.peop_lastnames).label('patient'),
            patient_alias.peop_dni.label('dni'),
            patient_alias.peop_gender.label('gender'),
            patient_alias.peop_birthdate.label('birthdate'),
            doctor_alias.peop_id.label('doctor_id'),
            PeoplePrescription.pepr_dx.label('diagnostic'),
            (doctor_alias.peop_names + ' ' +
             doctor_alias.peop_lastnames).label('doctor'),
            PeoplePrescription.pepr_created_at.label('created_at')
        ).join(patient_alias, PeoplePrescription.pepr_peop_id == patient_alias.peop_id).join(doctor_alias, PeoplePrescription.pepr_doct_id == doctor_alias.peop_id).filter(patient_alias.peop_dni == people).order_by(PeoplePrescription.pepr_id.desc()).first()
        photo = None
        medications = None
        patient = None
        medicine = None
        if consultation is not None:
            photo = PeoplePhotos.query.filter(PeoplePhotos.peph_peop_id==consultation.patient_id).order_by(PeoplePhotos.peph_id.desc()).first()
            medications = PeoplePrescriptionDetails.query.filter(PeoplePrescriptionDetails.prde_pepr_id == consultation.consultation, PeoplePrescriptionDetails.prde_dispatched == None).all()
            patient = [
                {
                        "patient": consultation.patient,
                        "patient_dni": consultation.dni,
                        "last_consultation": consultation.created_at.strftime("%d/%m/%Y"),
                        "doctor": consultation.doctor,
                    }
            ]
            medicine = [{
                        "medicina": med.prde_medicine,
                        "id": med.prde_id
                    } for med in medications]
        return [
            {
                "patient": patient if patient is not None else None,
                "medication": medicine,
                "photo": photo.peph_path if photo is not None else '27002.jpg'
            }
        ]

    def calcular_edad(fecha_nacimiento):
    # Obtiene la fecha de hoy
        fecha_hoy = date.today()

        # Obtiene la diferencia de años entre las dos fechas
        diferencia_de_anios = fecha_hoy.year - fecha_nacimiento.year

        # Verifica si la fecha de hoy es menor que la fecha de nacimiento
        if fecha_hoy < fecha_nacimiento:
            # La fecha de hoy aún no ha llegado, por lo que la edad es la diferencia de años menos 1
            edad = diferencia_de_anios - 1
        else:
            # La fecha de hoy ya ha llegado, por lo que la edad es la diferencia de años
            edad = diferencia_de_anios

        # Verifica si la fecha de hoy es menor que la fecha de nacimiento
        if fecha_hoy.month < fecha_nacimiento.month:
            # La fecha de hoy aún no ha llegado al mes de cumpleaños, por lo que la edad es la diferencia de años menos 1
            edad = edad - 1
        elif fecha_hoy.day < fecha_nacimiento.day:
            # La fecha de hoy aún no ha llegado al día de cumpleaños, por lo que la edad es la diferencia de años menos 1
            edad = edad - 1
        return edad
    
    def save_photo(form):
        # Obtener la imagen del formulario
        photo = form.capturedImage.data

        # Generar un nombre único para la imagen
        filename = f'{uuid.uuid4()}.jpg'

        # Guardar la imagen en la carpeta `static/uploads`
        with open(f'static/uploads/{filename}', 'wb') as f:
            f.write(photo.read())

        return filename
