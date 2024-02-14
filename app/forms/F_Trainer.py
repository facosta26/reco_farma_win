from flask_wtf import FlaskForm
from wtforms import HiddenField
class F_Trainer(FlaskForm):
    honeypot = HiddenField("Honeypot")
