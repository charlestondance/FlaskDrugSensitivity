from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from flask import current_app
from . import db, login_manager
import csv

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {'User': ( Permission.MAKE_LIST, True),
                 'SuperUser' : ( Permission.MAKE_LIST | Permission.EDIT_DB, False),
                 'Administrator' : (0xFF, False)
                 }

        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, permissions):
        return self.role is not None and \
                (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def __repr__(self):
        return '<User %r>' % self.username

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

class Permission:
    EDIT_DB = 0x01
    MAKE_LIST = 0x02
    ADMINISTER = 0x80

class CompoundDB(db.Model):
    __tablename__ = 'compoundsdb'

    id = db.Column(db.Integer, primary_key=True)
    formatted_batch_id = db.Column(db.String(64), unique=True, index=True)
    supplier = db.Column(db.String(64), unique=False, index=True)
    supplier_ref = db.Column(db.String(64), unique=False, index=True)
    well_ref = db.Column(db.String(64), unique=False, index=True)
    barcode = db.Column(db.String(64), unique=False, index=True)
    starting_concentration = db.Column(db.String(64), unique=False, index=True)
    concentration_range = db.Column(db.String(64), unique=False, index=True)

    @staticmethod
    def upload_csv(filename):
        with open(filename, newline='') as csvfile:
            read_source = csv.reader(csvfile, delimiter=',')
            for row in read_source:
                if row[0] == 'FORMATTED_BATCH_ID':
                    continue
                else:
                compound_add = CompoundDB(formatted_batch_id=row[0], supplier=row[1], supplier_ref=row[2], well_ref=row[3], barcode=row[4], starting_concentration=row[5], concentration_range=row[6])
                db.session.add(compound_add)

        db.session.commit()

    def __repr__(self):
        return '<compound_id %r>' % self.id

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
