from flask import render_template, redirect, request, url_for, flash
from .forms import LoginForm, RegistrationForm, DeleteUser
from flask.ext.login import login_user, logout_user, login_required
from . import auth
from .. import db
from ..models import User


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
@login_required
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

@auth.route('/user_management', methods=['GET'])
@login_required
def user_management():
    user_list = User.query.all()

    return render_template('auth/user_management.html', user_list=user_list)

@auth.route('/delete_user', methods=['GET', 'POST'])
@login_required
def delete_user():
    form = DeleteUser()

    if form.validate_on_submit():
        flash('Delete User')
        user_del = User.query.filter_by(username=form.username.data).first()
        db.session.delete(user_del)
        db.session.commit()
        return redirect(url_for('main.index'))

    return render_template('auth/delete_user.html', form=form)


