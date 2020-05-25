from flask_login import UserMixin,AnonymousUserMixin,current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask import abort
db = SQLAlchemy()

class Auth:
    READ = 1
    ADD = 2
    UPDATE = 4
    DELETE = 8
    HYPER = 16
    ADMIN = 31  # super = 11111
    # 可以进行所有操作并查看后台程序


class Caregiver(db.Model):
    __tablename__ = 'caregiver'
    cgid = db.Column(db.Integer,primary_key=True)
    label = db.Column(db.String(15))
    row_id = db.Column(db.Integer)
    description = db.Column(db.String(30))
    def __repr__(self):
        return "<cgid>:{0}".format(self.cgid)
    def __init__(self,**kwargs):
        for name,var in kwargs.items():
            self.__dict__[name] = var

class Patient(db.Model):
    __tablename__ = 'patients'
    row_id = db.Column(db.Integer)
    subject_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    gender = db.Column(db.String(5))
    dob = db.Column(db.DateTime)
    dod = db.Column(db.DateTime)
    dod_hosp = db.Column(db.DateTime)
    dod_ssn = db.Column(db.DateTime)
    expire_flag = db.Column(db.String(20))

    labs = db.relationship('LabEvent',backref='patient',cascade='all, delete-orphan')
    events = db.relationship('DataTimeEvent',backref='patient',cascade='all, delete-orphan')
    prescriptions = db.relationship('Prescription',backref='patient',cascade='all, delete-orphan')
    def __repr__(self):
        return "ID:<%r>" % self.subject_id


class Admission(db.Model):
    __tablename__ = 'admissions'
    row_id = db.Column(db.Integer,primary_key=True)
    subject_id = db.Column(db.Integer)
    hadm_id = db.Column(db.Integer)
    admittime = db.Column(db.DateTime)
    dischtime = db.Column(db.DateTime)
    deathtime = db.Column(db.DateTime)
    admission_type = db.Column(db.String(50))
    admission_location = db.Column(db.String(50))
    discharge_location = db.Column(db.String(50))
    insurance = db.Column(db.String(255))
    language = db.Column(db.String(10))
    religion = db.Column(db.String(50))
    marital_status = db.Column(db.String(50))
    ethnichity = db.Column(db.String(50))
    edregtime = db.Column(db.DateTime)
    edouttime = db.Column(db.DateTime)
    diagnosis = db.Column(db.String(50))
    hospital_expire_flag = db.Column(db.SmallInteger)
    has_chartevents_data = db.Column(db.SmallInteger)

    def __repr__(self):
        return "admit_time:{0},subject_id:{1}".format(self.admittime,self.subject_id)

class Cpt(db.Model):
    __tablename__ = 'cpt'
    row_id = db.Column(db.Integer,primary_key=True)
    subject_id = db.Column(db.Integer)
    hadm_id = db.Column(db.Integer)
    costcenter = db.Column(db.String(10))
    chartdate = db.Column(db.DateTime)
    cpt_cd = db.Column(db.String(15))
    cpt_number = db.Column(db.Integer)
    cpt_suffix = db.Column(db.String(5))
    ticket_id_seq = db.Column(db.Integer)
    sectionheader = db.Column(db.String(50))
    subsectionheader = db.Column(db.String(300))
    description = db.Column(db.String(200))

class d_cpt(db.Model):
    __tablename__ = 'd_cpt'
    row_id = db.Column(db.Integer,primary_key=True)
    category = db.Column(db.SmallInteger)
    sectionrange = db.Column(db.String(100))
    sectionheader = db.Column(db.String(50))
    subsectionrange = db.Column(db.String(100))
    subsectionheade = db.Column(db.String(100))
    codesuffix = db.Column(db.String(300))
    mincodeinsubsection = db.Column(db.Integer)
    maxcodeinsubsection = db.Column(db.Integer)

class d_labitems(db.Model):
    __tablename__ = 'd_labitems'
    row_id = db.Column(db.Integer)
    itemid = db.Column(db.Integer,primary_key=True)
    label = db.Column(db.String(100))
    fluid = db.Column(db.String(100))
    category = db.Column(db.String(100))
    loinc = db.Column(db.String(100))
    labs = db.relationship('LabEvent',backref='d_labs',lazy='dynamic')

class DataTimeEvent(db.Model):
    __tablename__ = "datatimeevent"
    row_id = db.Column(db.Integer,primary_key=True)
    subject_id = db.Column(db.Integer,db.ForeignKey('patients.subject_id',ondelete='CASCADE'))
    hadm_id = db.Column(db.Integer)
    icustay_id = db.Column(db.Integer)
    itemid = db.Column(db.Integer)
    charttime = db.Column(db.DateTime)
    storetime = db.Column(db.DateTime)
    cgid = db.Column(db.Integer)
    value = db.Column(db.DateTime)
    valueuom = db.Column(db.String(50))
    warning = db.Column(db.SmallInteger)
    error = db.Column(db.SmallInteger)
    resultstatus = db.Column(db.String(50))
    stopped = db.Column(db.String(50))



class LabEvent(db.Model):
    __tablename__ = 'labevents'
    row_id = db.Column(db.Integer,primary_key=True)
    subject_id = db.Column(db.Integer,db.ForeignKey('patients.subject_id',ondelete ='CASCADE'))
    hadm_id = db.Column(db.Integer)
    itemid = db.Column(db.Integer,db.ForeignKey('d_labitems.itemid'))
    charttime = db.Column(db.DateTime)
    value = db.Column(db.String(200))
    valuenum = db.Column(db.Numeric)
    valueuom = db.Column(db.String(20))
    flag = db.Column(db.String(20))


class Prescription(db.Model):
    __tablename__ = "prescription"
    row_id = db.Column(db.Integer,primary_key=True)
    subject_id = db.Column(db.Integer,db.ForeignKey('patients.subject_id',ondelete = "CASCADE"))
    hadm_id = db.Column(db.Integer)
    icustay_id = db.Column(db.Integer)
    startdate = db.Column(db.DateTime)
    enddate = db.Column(db.DateTime)
    drug_type = db.Column(db.String(120))
    drug = db.Column(db.String(120))
    drug_name_po = db.Column(db.String(120))
    drug_name_ge  = db.Column(db.String(120))
    formulary_drug  = db.Column(db.String(120))
    gsn = db.Column(db.String(120))
    ndc = db.Column(db.String(120))
    prod_strength = db.Column(db.String(120))
    dose_val_rx = db.Column(db.String(120))
    dose_unit_rx = db.Column(db.String(120))
    form_val_disp  = db.Column(db.String(120))
    form_unit_disp  = db.Column(db.String(120))
    route = db.Column(db.String(120))
    def __init__(self,kwargs):
        for caption,val in kwargs.items():
            self.__dict__[caption] = val
            print(caption,val)
    def update(self,name,var):
        if self.__dict__[name] != None:
            self.__dict__[name] = var
        else:
            print("Attribute not exist")
#

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    name = db.Column(db.String(64),unique=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User',backref='role',lazy='dynamic')
    @staticmethod
    def insert_roles():
        roles = {
            'assistance' : Auth.READ,
            'doctor' : (Auth.READ | Auth.UPDATE | Auth.ADD),
            'admin': Auth.ADMIN
        }
        for r in roles:
            print(r)
            role = Role.query.filter_by(name=r).first()
            if Role is None:
                role = Role(name=r)
            role.Permissions = roles[r]
            db.session.add(role)
        db.session.commit()


class User(db.Model,UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer,primary_key= True,autoincrement=True)
    Email = db.Column(db.String(50))
    permission = db.Column(db.Integer)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    pwd = db.Column(db.String(50))
    name = db.Column(db.String(30))
    password_hash = db.Column(db.String(128))

    def can(self,permissions):
        print("CAN",self.role.permissions,permissions,self.role.permissions & permissions)
        return self.role.permissions is not None and \
                (self.role.permissions & permissions) == permissions
    @property
    def password(self):
        raise AttributeError('Not readable')
    @password.setter
    def password(self,password):
        self.pwd = password
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __init__(self,**kwargs):
        for name,var in kwargs.items():
            self.__dict__[name] = var

    def __repr__(self):
        return "<name>:{0}".format(self.name)

class AnoymousUser(AnonymousUserMixin):
    def can(self,permissions):
        return False

#decorator
def permission_required(permisson):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            if not current_user.can(permisson):
                print("ABORT")
                abort(403)
            return f(*args,**kwargs)
        return decorated_function
    return decorator


