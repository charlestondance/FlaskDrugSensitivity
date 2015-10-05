from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

class RegistrationForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                           Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    password = PasswordField('Password', validators=[
        Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class AddCompound(Form):
    formatted_batch_id = StringField('Batch ID', validators=[Required(), Length(1, 64)])
    supplier = StringField('supplier', validators=[Required(), Length(1, 64)])
    supplier_ref = StringField('supplier_ref', validators=[Required(), Length(1, 64)])
    well_ref = StringField('well_ref', validators=[Required(), Length(1, 64)])
    barcode = StringField('barcode', validators=[Required(), Length(1, 64)])
    starting_concentration = StringField('starting_concentration', validators=[Required(), Length(1, 64)])
    concentration_range = StringField('concentrationrange', validators=[Required(), Length(1, 64)])
    submit = SubmitField('SubmitCompound')

class DeleteCompound(Form):
    formatted_batch_id = StringField('Batch ID', validators=[Required(), Length(1, 64)])
    submit = SubmitField('DeleteCompound')

class Hitlist(Form):
    hitlist = TextAreaField("Paste in list of compounds", validators=[Required()])
    copies = IntegerField("How many sets", validators=[Required()])
    name = TextAreaField("Destination Set Name", validators=[Required()])
    submit = SubmitField('Submit')