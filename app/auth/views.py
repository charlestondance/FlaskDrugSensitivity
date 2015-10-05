from flask import render_template, redirect, request, url_for, flash, make_response
from flask.ext.login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import User, CompoundDB
from .forms import LoginForm, RegistrationForm, AddCompound, DeleteCompound, Hitlist
from .. import db
from . generate_hitlist import make_hitlist
from flask.ext import excel


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now login')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/testing', methods=['GET'])
@login_required
def testing():
    print('hi')
    return render_template('auth/testing.html')

@auth.route('/showcompound', methods=['GET'])
@login_required
def show_compound():
    compound = CompoundDB.query.all()
    print(compound)
    print('showcompound')
    return render_template('auth/showcompound.html', compound=compound)

@auth.route('/registercompound', methods=['GET', 'POST'])
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

    return render_template('auth/registercompound.html', form=form)

@auth.route('/deletecompound', methods=['GET', 'POST'])
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

    return render_template('auth/registercompound.html', form=form)

@auth.route('/hitlist', methods=['GET', 'POST'])
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

        output = excel.make_response_from_array(output_list, 'csv')
        output.headers["Content-Disposition"] = "attachment; filename=export.csv"
        output.headers["Content-type"] = "text/csv"
        flash("Done!")
        return output


    return render_template('auth/pastehitlist.html', form=form)