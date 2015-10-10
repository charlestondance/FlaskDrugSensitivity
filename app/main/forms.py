from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError

class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

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
