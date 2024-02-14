from datetime import datetime
from flask import Blueprint, json, render_template, request, session
from app.forms.F_People import F_Busqueda_Persona

from app.forms.F_Pharma import F_Deliver_Medications
from app.models.Models import db, PeoplePrescriptionDetails
from app.utils.utils import check_role


class C_Pharma():
    pharma = Blueprint('pharma', __name__)
    
    @pharma.route('/medical_prescriptions')
    @check_role(['FARMACEUTICO'])
    def medical_prescriptions():
        form = F_Deliver_Medications()
        formBusq = F_Busqueda_Persona()
        return render_template('v_medical_prescriptions.html', title="Ver Prescripciones Médicas", form=form, formBusq=formBusq)
    
    @pharma.route('/deliver_medication', methods=['POST'])
    @check_role(['FARMACEUTICO'])
    def deliver_medication():
        message = {"correcto": '', "alerta": '', "error": '', 'delivered': []}
        deliver = request.form.getlist("txtMedicina")
        parcel_types = request.form.getlist("sltTipoEmpaque")
        quantity = request.form.getlist("txtCantMedicina")
        print(len(deliver))
        print(len(parcel_types))
        print(len(quantity))
        if len(deliver) > 0 and len(parcel_types) > 0 and len(quantity) > 0:
                for i, d in enumerate(deliver):
                    if int(quantity[i]) > 0:
                        prescription = PeoplePrescriptionDetails.query.filter_by(prde_id=d).first()
                        if prescription.prde_dispatched!='S':
                            prescription.prde_dispatched = "S"
                            prescription.prde_parcel_type_id = parcel_types[i]
                            prescription.prde_quantity = quantity[i]
                            prescription.prde_date_dispatched = datetime.now()
                            prescription.prde_user_dispatcher_id = session['user_id']
                            prescription.prde_user_updated_id = session['user_id']
                            db.session.commit()
                            message['delivered'].append(d)
                        else:
                            message['alerta'] = "Ya se ha entregado este medicamento"
                            return json.dumps(message)
                message["correcto"] = "Los medicamentos han sido entregados correctamente"
        else:
            message["alerta"] = "Debe seleccionar al menos un medicamento"
        return json.dumps(message)