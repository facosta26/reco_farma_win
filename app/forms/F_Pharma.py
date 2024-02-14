from flask_wtf import FlaskForm
from wtforms import HiddenField

class F_Deliver_Medications(FlaskForm):
    txtHoneyPot = HiddenField('Pote de miel')