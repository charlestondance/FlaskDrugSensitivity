from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, SelectField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import Role, User

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
    submit = SubmitField('Delete Compound')

class SearchCompound(Form):
    formatted_batch_id = StringField('Batch ID', validators=[Required(), Length(1, 64)])
    submit = SubmitField('Search Compound')

class Hitlist(Form):

    hitlist = TextAreaField("Paste in list of compounds", validators=[Required()])
    copies = IntegerField("How many sets", validators=[Required()])
    name = StringField("Destination Set Name", validators=[Required(), Length(1, 9)])
    role = SelectField('Export File for', coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(Hitlist, self).__init__(*args, **kwargs)
        self.role.choices = [(1, "Echo"), (2, "Barcode")]

class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    username = StringField('Username', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                    'Usernames must have only letters, '
                                                   'numbers, dots or underscores')])

    role = SelectField('Role', coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.fileter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class EditCompound(Form):

    starting_concentration = SelectField('Starting Plate', coerce=int)
    concentration_range = SelectField('Concentration range', coerce=str)
    submit = SubmitField('EditCompound')



    def __init__(self, compound, *args, **kwargs):
        super(EditCompound, self).__init__(*args, **kwargs)
        self.concentration_range.choices = [("A", "A"), ("B", "B")]
        self.starting_concentration.choices = [(0, 0), (1, 1), (2, 2), (3, 3)]

        self.compound = compound

class CombinationHitlist(Form):

    hitlist = TextAreaField("Paste in list of compounds", validators=[Required()])
    hitlist2 = TextAreaField("Paste in list of compounds", validators=[Required()])
    hitlist3 = TextAreaField("Paste in list of compounds")
    hitlist4 = TextAreaField("Paste in list of compounds")
    copies = IntegerField("How many sets", validators=[Required()])
    name = StringField("Destination Set Name", validators=[Required(), Length(1, 9)])

    submit = SubmitField('Submit')


