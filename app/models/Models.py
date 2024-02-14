from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.utils import asuncion_timezone
db = SQLAlchemy()

class Roles(db.Model):
    __tablename__ = 'roles'
    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_desc = db.Column(db.String(100), unique=True, nullable=False)


class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(10), unique=True, nullable=False)
    user_password = db.Column(db.String(255), nullable=False)
    user_state = db.Column(db.String(1), default='A')
    user_role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    user_created_at = db.Column(db.DateTime, default=datetime.now(asuncion_timezone))
    user_created_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    user_updated_at = db.Column(db.DateTime, onupdate=datetime.now(asuncion_timezone))
    user_updated_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    user_peop_id = db.Column(db.Integer, db.ForeignKey('people.peop_id'))
    user_register = db.relationship(
        'Users', backref='users_register', foreign_keys=[user_created_id], remote_side=[user_id])
    user_modifier = db.relationship(
        'Users', backref='users_modifier', foreign_keys=[user_updated_id], remote_side=[user_id])
    
    def hash_password(password):
        return generate_password_hash(password)
    def check_password_hash(password_hash,contrasena):
        return check_password_hash(password_hash, contrasena)
    def is_active(self):
        return self.user_state
    
    def get_id(self):
        return self.user_id
    
class Parcel_Type(db.Model):
    __tablename__ = 'parcel_type'
    paty_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paty_desc = db.Column(db.String(100), unique=True, nullable=False)
    paty_created_at = db.Column(db.DateTime, default=datetime.now(asuncion_timezone))
    paty_user_created_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    paty_updated_at = db.Column(db.DateTime, onupdate=datetime.now(asuncion_timezone))
    paty_user_updated_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    paty_state = db.Column(db.String(1), default="A", nullable=False)
    paty_register = db.relationship(
        'Users', backref='paty_register', foreign_keys=[paty_user_created_id])
    paty_modifier = db.relationship(
        'Users', backref='paty_modifier', foreign_keys=[paty_user_updated_id])

class People(db.Model):
    __tablename__ = 'people'
    peop_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    peop_names = db.Column(db.String(100), nullable=False)
    peop_lastnames = db.Column(db.String(100), nullable=False)
    peop_dni = db.Column(db.String(8), unique=True, nullable=False)
    peop_gender = db.Column(db.String(1), nullable=False)
    peop_birthdate = db.Column(db.Date(), nullable=False)
    peop_created_at = db.Column(db.DateTime, default=datetime.now(asuncion_timezone))
    peop_user_created_id = db.Column(
        db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    peop_updated_at = db.Column(db.DateTime, onupdate=datetime.now(asuncion_timezone))
    peop_user_updated_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    peop_register = db.relationship(
        'Users', backref='peop_register', foreign_keys=[peop_user_created_id])
    peop_modifier = db.relationship(
        'Users', backref='peop_modifier', foreign_keys=[peop_user_updated_id])
    
class Institutions(db.Model):
        __tablename__ = "institutions"
        inst_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        inst_bussiness_name = db.Column(db.String(200), nullable=False)
        inst_trade_name = db.Column(db.String(200), nullable=False)
        inst_itin = db.Column(db.String(30), nullable=False)
        inst_state = db.Column(db.String(1), default='A', nullable=False)
        inst_created_at = db.Column(db.DateTime, default=datetime.now(asuncion_timezone))
        inst_user_created_id = db.Column(
            db.Integer, db.ForeignKey('users.user_id'), nullable=False)
        inst_updated_at = db.Column(db.DateTime, onupdate=datetime.now(asuncion_timezone))
        inst_user_updated_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
        inst_register = db.relationship(
            'Users', backref='inst_register', foreign_keys=[inst_user_created_id])
        inst_modifier = db.relationship(
            'Users', backref='inst_modifier', foreign_keys=[inst_user_updated_id])
        
        __table_args__ = (
            db.UniqueConstraint('inst_bussiness_name', 'inst_trade_name',
                                'inst_itin', name='uq_institution_info'),
        )

class MedicalEspecialties(db.Model):
    __tablename__ = "medical_especialties"
    mees_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mees_desc = db.Column(db.String(100), nullable=False, unique=True)
    mees_state = db.Column(db.String(1), default='A', nullable=False)
    mees_created_at = db.Column(db.DateTime, default=datetime.now(asuncion_timezone))
    mees_user_created_id = db.Column(
        db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    mees_updated_at = db.Column(db.DateTime, onupdate=datetime.now(asuncion_timezone))
    mees_user_updated_id = db.Column(
        db.Integer, db.ForeignKey('users.user_id'))
    mees_register = db.relationship(
        'Users', backref='mees_register', foreign_keys=[mees_user_created_id])
    mees_modifier = db.relationship(
        'Users', backref='mees_modifier', foreign_keys=[mees_user_updated_id])

class Doctors(db.Model):
    __tablename__ = "doctors"
    doct_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doct_peop_id = db.Column(db.Integer, db.ForeignKey('people.peop_id'), nullable=False)
    doct_professional_registration = db.Column(db.String(20), nullable=False)
    doct_mees_id = db.Column(db.Integer, db.ForeignKey('medical_especialties.mees_id'))
    doct_inst_id = db.Column(db.Integer, db.ForeignKey('institutions.inst_id'))
    doct_state = db.Column(db.String(1), default='A', nullable=False)
    doct_created_at = db.Column(db.DateTime, default=datetime.now(asuncion_timezone))
    doct_user_created_id = db.Column(
        db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    doct_updated_at = db.Column(db.DateTime, onupdate=datetime.now(asuncion_timezone))
    doct_user_updated_id = db.Column(
        db.Integer, db.ForeignKey('users.user_id'))
    doct_register = db.relationship(
        'Users', backref='doct_register', foreign_keys=[doct_user_created_id])
    doct_modifier = db.relationship(
        'Users', backref='doct_modifier', foreign_keys=[doct_user_updated_id])
    
class Pharmacist(db.Model):
    __tablename__ = "pharmacist"
    phar_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phar_peop_id = db.Column(db.Integer, db.ForeignKey(
        'people.peop_id'), nullable=False)
    phar_inst_id = db.Column(db.Integer, db.ForeignKey('institutions.inst_id'))
    phar_state = db.Column(db.String(1), default='A', nullable=False)
    phar_created_at = db.Column(db.DateTime, default=datetime.now(asuncion_timezone))
    phar_user_created_id = db.Column(
        db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    phar_updated_at = db.Column(db.DateTime, onupdate=datetime.now(asuncion_timezone))
    phar_user_updated_id = db.Column(
        db.Integer, db.ForeignKey('users.user_id'))
    phar_register = db.relationship(
        'Users', backref='phar_register', foreign_keys=[phar_user_created_id])
    phar_modifier = db.relationship(
        'Users', backref='phar_modifier', foreign_keys=[phar_user_updated_id])

class PeoplePrescription(db.Model):
    __tablename__ = "people_prescription"
    pepr_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pepr_dx = db.Column(db.String(4000))
    pepr_peop_id = db.Column(db.Integer, db.ForeignKey('people.peop_id'), nullable=False)
    pepr_doct_id = db.Column(db.Integer, db.ForeignKey('doctors.doct_id'), nullable=False)
    pepr_state = db.Column(db.String(1), default='A', nullable=False)
    pepr_created_at = db.Column(db.DateTime, default=datetime.now(asuncion_timezone))
    pepr_user_created_id = db.Column(
        db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    pepr_updated_at = db.Column(db.DateTime, onupdate=datetime.now(asuncion_timezone))
    pepr_user_updated_id = db.Column(
        db.Integer, db.ForeignKey('users.user_id'))
    pepr_register = db.relationship(
        'Users', backref='pepr_register', foreign_keys=[pepr_user_created_id])
    pepr_modifier = db.relationship(
        'Users', backref='pepr_modifier', foreign_keys=[pepr_user_updated_id])

class PeoplePrescriptionDetails(db.Model):
    __tablename__ = "people_prescription_details"
    prde_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prde_pepr_id = db.Column(db.Integer, db.ForeignKey('people_prescription.pepr_id'), nullable=False)
    prde_medicine = db.Column(db.String(100), nullable=False)
    prde_medical_indications = db.Column(db.String(4000), nullable=False)
    prde_state = db.Column(db.String(1), default='A', nullable=False)
    prde_date_dispatched = db.Column(db.DateTime)
    prde_user_dispatcher_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    prde_dispatched = db.Column(db.String(1))
    prde_paty_id = db.Column(db.Integer, db.ForeignKey('parcel_type.paty_id'))
    prde_quantity = db.Column(db.Integer)
    prde_created_at = db.Column(db.DateTime, default=datetime.now(asuncion_timezone))
    prde_user_created_id = db.Column(
        db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    prde_updated_at = db.Column(db.DateTime, onupdate=datetime.now(asuncion_timezone))
    prde_user_updated_id = db.Column(
        db.Integer, db.ForeignKey('users.user_id'))
    prde_register = db.relationship(
        'Users', backref='prde_register', foreign_keys=[prde_user_created_id])
    prde_modifier = db.relationship(
        'Users', backref='prde_modifier', foreign_keys=[prde_user_updated_id])
    prde_dispatcher = db.relationship(
        'Users', backref='prde_dispatcher', foreign_keys=[prde_user_dispatcher_id])
    
class PeoplePhotos(db.Model):
    __tablename__ = 'people_photos'
    peph_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    peph_path = db.Column(db.String(100), nullable=False)
    peph_peop_id = db.Column(db.Integer, db.ForeignKey('people.peop_id'), nullable=False)
    peph_state = db.Column(db.String(1), default='A', nullable=False)
    peph_created_at = db.Column(db.DateTime, default=datetime.now(asuncion_timezone))
    peph_user_created_id = db.Column(
        db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    peph_updated_at = db.Column(db.DateTime, onupdate=datetime.now(asuncion_timezone))
    peph_user_updated_id = db.Column(
        db.Integer, db.ForeignKey('users.user_id'))
    peph_register = db.relationship(
        'Users', backref='peph_register', foreign_keys=[peph_user_created_id])
    peph_modifier = db.relationship(
        'Users', backref='peph_modifier', foreign_keys=[peph_user_updated_id])
