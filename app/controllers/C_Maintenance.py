#Run pip install flask-blueprint
from flask import Blueprint, json, render_template, request, session
from app.forms.F_Maintenance import F_Especialidad_Medica, F_Instituciones_Medicas, F_Tipos_Empaques
from app.models.Models import Parcel_Type, db, Institutions, MedicalEspecialties
from app.utils.utils import check_role
class C_Maintenance():
    maint = Blueprint('maint',__name__)
    
    @maint.route('/maintenance')
    @check_role(['ADMINISTRADOR'])
    def maintenance():
        fme = F_Especialidad_Medica()
        fmi = F_Instituciones_Medicas()
        fte = F_Tipos_Empaques()
        return render_template('v_maintenance.html', title="Mantenimiento de Datos", fme=fme, fmi=fmi, fte=fte)
    
    @maint.route('/get_medical_especialties')
    @check_role(['ADMINISTRADOR'])
    def get_medical_especialties():
        medical_especialties = MedicalEspecialties.query.order_by(MedicalEspecialties.mees_desc).paginate(
            page=request.args.get('page', 1), per_page=10)
        return json.dumps([{
            "id": mees.mees_id,
            "desc": mees.mees_desc,
            "state": mees.mees_state,
            "state_desc": "ACTIVO" if mees.mees_state =="A" else "INACTIVO",
        } for mees in medical_especialties
        ])
        
    @maint.route('/get_medical_institutes')
    @check_role(['ADMINISTRADOR'])
    def get_medical_institutes():
        medical_institutes = Institutions.query.order_by(Institutions.inst_trade_name).paginate(
            page=request.args.get('page', 1), per_page=10)
        return json.dumps([{
            "id": inst.inst_id,
            "trade_name": inst.inst_trade_name,
            "bussiness_name": inst.inst_bussiness_name,
            "itin": inst.inst_itin,
            "state": inst.inst_state,
            "state_desc": "ACTIVO" if inst.inst_state =="A" else "INACTIVO",
        } for inst in medical_institutes
        ])
    
    @maint.route('/get_parcel_types/<total>')    
    @maint.route('/get_parcel_types')
    @check_role(['ADMINISTRADOR', 'FARMACEUTICO'])
    def get_parcel_types(total=False):
        if total!=False:
            parcel_types = Parcel_Type.query.order_by(Parcel_Type.paty_desc).all()
        else:
            parcel_types = Parcel_Type.query.order_by(Parcel_Type.paty_desc).paginate(
            page=request.args.get('page', 1), per_page=10)
        return json.dumps([{
            "id": paty.paty_id,
            "desc": paty.paty_desc,
            "state": paty.paty_state,
            "state_desc": "ACTIVO" if paty.paty_state =="A" else "INACTIVO",
        } for paty in parcel_types
        ])
        
    @maint.route('/add_medical_especialties', methods=['POST'])
    def add_medical_especialties():
        message = {"correcto": '', "alerta": '', "error": ''}
        form = F_Especialidad_Medica(request.form)
        if form.validate_on_submit():
            id = form.txtMEcod.data
            try:
                exist = MedicalEspecialties.query.filter_by(mees_desc = form.txtDescripcionME.data, mees_state = form.sltEstadoME.data).first()
                if exist is None:
                    if id != "":
                        especialidad = MedicalEspecialties.query.filter(MedicalEspecialties.mees_id==id).first()
                        especialidad.mees_desc = (form.txtDescripcionME.data).upper()
                        especialidad.mees_state = form.sltEstadoME.data
                        especialidad.mees_user_updated_id = session['user_id']
                        db.session.commit()
                        message['correcto'] = "Se ha actualizado la especialidad"
                    else:
                        especialidad = MedicalEspecialties()
                        especialidad.mees_desc = (form.txtDescripcionME.data).upper()
                        especialidad.mees_state = form.sltEstadoME.data
                        especialidad.mees_user_created_id = session['user_id']
                        db.session.add(especialidad)
                        db.session.commit()
                        message['correcto'] = "Se ha registrado la especialidad"
                else:
                    message['alerta'] = "Ya existe una especialidad con esos datos."
            
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
    
    @maint.route('/add_medical_institutes', methods=['POST'])
    @check_role(['ADMINISTRADOR'])
    def add_medical_institutes():
        message = {"correcto": '', "alerta": '', "error": ''}
        form = F_Instituciones_Medicas(request.form)
        if form.validate_on_submit():
            id = form.txtIMcod.data
            trade_name = (form.txtNombreFantasiaIM.data).upper()
            bussiness_name = (form.txtRazonSocialIM.data).upper()
            itin = form.txtItinIM.data
            state = form.sltEstadoIM.data
            try:
                exist = Institutions.query.filter(Institutions.inst_trade_name == trade_name, Institutions.inst_bussiness_name == bussiness_name, Institutions.inst_itin == itin, Institutions.inst_state == state).first()
                if exist is None:
                    if id != "":
                        institucion = Institutions.query.filter(Institutions.inst_id==id).first()
                        institucion.inst_trade_name = trade_name
                        institucion.inst_bussiness_name = bussiness_name
                        institucion.inst_itin = itin
                        institucion.inst_state = state
                        institucion.inst_user_updated_id = session['user_id']
                        db.session.commit()
                        message['correcto'] = "Se ha actualizado la institución"
                    else:
                        institucion = Institutions()
                        institucion.inst_trade_name = trade_name
                        institucion.inst_bussiness_name = bussiness_name
                        institucion.inst_itin = itin
                        institucion.inst_state = state
                        institucion.inst_user_created_id = session['user_id']
                        db.session.add(institucion)
                        db.session.commit()
                        message['correcto'] = "Se ha registrado la institución"
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
    
    @maint.route('/add_parcel_types', methods=['POST'])
    def add_parcel_types():
        message = {"correcto": '', "alerta": '', "error": ''}
        form = F_Tipos_Empaques(request.form)
        if form.validate_on_submit():
            id = form.txtTEcod.data
            try:
                exist = Parcel_Type.query.filter_by(paty_desc = form.txtDescripcionTE.data, paty_state = form.sltEstadoTE.data).first()
                if exist is None:
                    if id != "":
                        tipo_empaque = Parcel_Type.query.filter(Parcel_Type.paty_id==id).first()
                        tipo_empaque.paty_desc = (form.txtDescripcionTE.data).upper()
                        tipo_empaque.paty_state = form.sltEstadoTE.data
                        tipo_empaque.paty_user_updated_id = session['user_id']
                        db.session.commit()
                        message['correcto'] = "Se ha actualizado el tipo empaque"
                    else:
                        tipo_empaque = Parcel_Type()
                        tipo_empaque.paty_desc = (form.txtDescripcionTE.data).upper()
                        tipo_empaque.paty_state = form.sltEstadoTE.data
                        tipo_empaque.paty_user_created_id = session['user_id']
                        db.session.add(tipo_empaque)
                        db.session.commit()
                        message['correcto'] = "Se ha registrado el tipo empaque"
                else:
                    message['alerta'] = "Ya existe el tipo empaque con esos datos."
            
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