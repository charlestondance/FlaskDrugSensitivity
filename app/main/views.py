from flask import render_template,redirect, request, url_for, flash
from . import main
from ..models import CompoundDB
from .forms import AddCompound, DeleteCompound, Hitlist
from .. import db
from app.main.generate_hitlist import make_hitlist
from flask.ext import excel
import pyexcel.ext.xls
from flask.ext.login import login_required, current_user

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/showcompound', methods=['GET'])
@login_required
def show_compound():
    compound = CompoundDB.query.all()
    print(compound)
    print('showcompound')
    return render_template('showcompound.html', compound=compound)

@main.route('/registercompound', methods=['GET', 'POST'])
@login_required
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
def delete_compound():
    form = DeleteCompound()
    print('delete_compound')
    if form.validate_on_submit():
        flash('Compound deleted')
        compound_del = CompoundDB.query.filter_by(formatted_batch_id=form.formatted_batch_id.data).first()
        db.session.delete(compound_del)
        db.session.commit()
        return redirect(url_for('main.index'))

    return render_template('registercompound.html', form=form)

@main.route('/hitlist', methods=['GET', 'POST'])
@login_required
def hitlist():
    form = Hitlist()

    if form.validate_on_submit():
        flash('Hitlist')
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
        print(output_list)

        output = excel.make_response_from_array(output_list, 'xls')
        output.headers["Content-Disposition"] = "attachment; filename=export.xls"
        output.headers["Content-type"] = "text/csv"
        flash("Done!")
        return output


    return render_template('pastehitlist.html', form=form)