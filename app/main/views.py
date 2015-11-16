from flask import render_template,redirect, request, url_for, flash
from . import main
from ..models import CompoundDB, User, Role, Permission
from .forms import AddCompound, DeleteCompound, Hitlist, EditProfileAdminForm, EditCompound, SearchCompound, CombinationHitlist, UploadCSVfile
from .. import db
from app.main.generate_hitlist import make_hitlist, combination_make_hitlist
from flask.ext import excel
import pyexcel.ext.xls
from flask.ext.login import login_required, current_user
from ..decorators import admin_required, permission_required
from werkzeug import secure_filename

@main.route('/')
def index():
    return render_template('index.html', Permission=Permission)

@main.route('/showcompound', methods=['GET'])
@login_required
def show_compound():
    page = request.args.get('page', 1, type=int)
    pagination = CompoundDB.query.order_by(CompoundDB.id).paginate(page, per_page=20, error_out=False)
    print(pagination.items)
    compound = pagination.items
    #compound = CompoundDB.query.all()
    #return a value for the big jump for next page so long as it doesnt go over the maximum
    page_10 = pagination.next_num+9
    if page_10 > pagination.pages:
        pageincrement = pagination.pages
    else:
        pageincrement = page_10

    #check the decrease doesnt go below 1
    page_decrement = page - 10
    if page_decrement < 1:
        page_decrement = 1
    print(page_decrement)


    return render_template('showcompound.html', compound=compound, pagination=pagination, pageincrement=pageincrement, page_decrement=page_decrement)

@main.route('/registercompound', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.EDIT_DB)
def register_compound():
    form = AddCompound()
    print('register_compound')
    if form.validate_on_submit():
        flash('Compound added')
        compound_add = CompoundDB(formatted_batch_id=form.formatted_batch_id.data, supplier=form.supplier.data, supplier_ref=form.supplier_ref.data, well_ref=form.well_ref.data, barcode=form.barcode.data, starting_concentration=form.starting_concentration.data, concentration_range=form.concentration_range.data)
        db.session.add(compound_add)
        db.session.commit()

        return redirect(url_for('main.index'))

    return render_template('registercompound.html', form=form)

@main.route('/deletecompound', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.EDIT_DB)
def delete_compound():
    form = DeleteCompound()
    print('delete_compound')
    if form.validate_on_submit():

        compound_del = CompoundDB.query.filter_by(formatted_batch_id=form.formatted_batch_id.data).first()
        db.session.delete(compound_del)
        db.session.commit()
        flash('Compound deleted')
        return redirect(url_for('main.index'))

    return render_template('deletecompound.html', form=form)

@main.route('/hitlist', methods=['GET', 'POST'])
@login_required
def hitlist():
    form = Hitlist()

    if form.validate_on_submit():

        hitlist_store = (form.data['hitlist'])
        #split out the data into a list
        hitlist_list = hitlist_store.split('\r\n')
        db_hitlist = []
        for x in hitlist_list:
            #iterate through the list and search the db
            try:
                query_line_fromhitlist = CompoundDB.query.filter_by(formatted_batch_id=x).first()
                listio = (query_line_fromhitlist.formatted_batch_id, query_line_fromhitlist.barcode, query_line_fromhitlist.well_ref, query_line_fromhitlist.starting_concentration, query_line_fromhitlist.concentration_range)
                db_hitlist.append(listio)

            except:
                flash('didnt work - '+ x)
        output_list = make_hitlist(db_hitlist, form.data['copies'], form.data['name'])

        #the options are for 1=echo, just output the hitlist for echo
        if form.role.data == 1:

            output = excel.make_response_from_array(output_list, 'xls')
            output.headers["Content-Disposition"] = "attachment; filename=" + form.name.data + ".xls"
            output.headers["Content-type"] = "text/csv"
        else:
            #count the number of destination plates
            destination_barcodes = []
            destination_barcodes_for_out = []
            for x in output_list[1:]:
                destination_barcodes.append(x[5])
                #have to have two columns for export, barcode means nothing
                destination_barcodes_for_out.append(x[5])

            #make the barode list a set so it only has unique values
            destination_barcodes_for_out_set = list(set(destination_barcodes))
            print(destination_barcodes_for_out_set)
            make_2dlist = []
            for x in destination_barcodes_for_out_set:
                make_2dlist.append([x, "Barcode"])

            destination_plates = (len(set(destination_barcodes)))
            #count the number of source plates
            source_barcodes = []
            for x in output_list[1:]:
                source_barcodes.append(x[1])

            source_plates = (len(set(source_barcodes)))


            output = excel.make_response_from_array(make_2dlist, 'xls')
            output.headers["Content-Disposition"] = "attachment; filename=" + form.name.data + "_barcodes.xls"
            output.headers["Content-type"] = "text/csv"
            if destination_plates + source_plates > 82:
                flash("WARNING, the number of plates exceed system capacity (82) for set " + form.name.data + ".")

        flash("Done! " + form.name.data)
        return output


    return render_template('pastehitlist.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.role = Role.query.get(form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.role.data = user.role_id
    return render_template('edit_profile.html', form=form, user=user)

@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)

@main.route('/editcompound/<string:batch_id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.EDIT_DB)
def edit_compound(batch_id):
    """this will take the formatted batch id and allow the user to edit the compounds starting conc and range
    """

    compound = CompoundDB.query.filter_by(formatted_batch_id=batch_id).first_or_404()
    form = EditCompound(compound=compound)
    if form.validate_on_submit():
        compound.starting_concentration = form.starting_concentration.data
        compound.concentration_range = form.concentration_range.data
        db.session.commit()
        flash('Compound updated')
        return redirect(url_for('main.index'))

    #set the defaults
    form.starting_concentration.data = int(compound.starting_concentration)
    form.concentration_range.data = compound.concentration_range

    return render_template('edit_compound.html', form=form, compound=compound)

@main.route('/searchcompound', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.EDIT_DB)
def search_compound():
    """this will search the DB for the entered compound and return the edit page"""
    form = SearchCompound()
    if form.validate_on_submit():
        compound = form.formatted_batch_id.data
        return redirect(url_for('.edit_compound', batch_id = compound ))

    return render_template('searchcompound.html', form=form)

@main.route('/combinationhitlist', methods=['GET', 'POST'])
@login_required
def combinationhitlist():
    form = CombinationHitlist()

    if form.validate_on_submit():

        hitlist_store1 = (form.data['hitlist'])
        #split out the data into a list
        hitlist_list1 = hitlist_store1.split('\r\n')
        db_hitlist1 = []
        for x in hitlist_list1:
            #iterate through the list and search the db
            try:
                query_line_fromhitlist = CompoundDB.query.filter_by(formatted_batch_id=x).first()
                listio = (query_line_fromhitlist.formatted_batch_id, query_line_fromhitlist.barcode, query_line_fromhitlist.well_ref, query_line_fromhitlist.starting_concentration, query_line_fromhitlist.concentration_range)
                db_hitlist1.append(listio)

            except:
                flash('didnt work - '+ x)
        #second hitlist
        hitlist_store2 = (form.data['hitlist2'])
        #split out the data into a list
        hitlist_list2 = hitlist_store2.split('\r\n')
        db_hitlist2 = []
        for x in hitlist_list2:
            #iterate through the list and search the db
            try:
                query_line_fromhitlist = CompoundDB.query.filter_by(formatted_batch_id=x).first()
                listio = (query_line_fromhitlist.formatted_batch_id, query_line_fromhitlist.barcode, query_line_fromhitlist.well_ref, query_line_fromhitlist.starting_concentration, query_line_fromhitlist.concentration_range)
                db_hitlist2.append(listio)

            except:
                flash('didnt work - '+ x)

        output_list = combination_make_hitlist(db_hitlist1, db_hitlist2, form.data['copies'], form.data['name'])

        output = excel.make_response_from_array(output_list, 'xls')
        output.headers["Content-Disposition"] = "attachment; filename=" + form.name.data + ".xls"
        output.headers["Content-type"] = "text/csv"

        flash("Done! ")
        return output

    return render_template('combination_hitlist.html', form=form)

@main.route('/uploadcsv', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.EDIT_DB)
def uploadcsv():
    """upload csv files of compounds to the database"""
    form = UploadCSVfile()
    if form.validate_on_submit():
        filename = secure_filename(form.compounds.data.filename)
        form.compounds.data.save("app/uploads/" + filename)
        filename_read = "app/uploads/" + filename

        CompoundDB().upload_csv(filename_read)
        flash('Database updated')
        return redirect(url_for('main.index'))

    return render_template('uploadcsv.html', form=form)

