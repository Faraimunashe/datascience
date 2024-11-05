from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, login_user, logout_user
from . import db
from app.models import User
from app.forms import UserForm
from werkzeug.security import generate_password_hash, check_password_hash
from passlib.hash import sha256_crypt

users_bp = Blueprint('users', __name__)


@users_bp.route('/users', methods=['GET'])
@login_required
def users():
    users = User.query.all()
    return render_template('users.html', users=users)


@users_bp.route('/users/new', methods=['GET', 'POST'])
@login_required
def create_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('error email already exists!')
            return redirect(url_for('users.create_user'))
        hashed_password = sha256_crypt.encrypt(form.password.data)
        new_user = User(
            email=form.email.data,
            password=hashed_password,
            name=form.name.data,
            role=1
        )

        db.session.add(new_user)
        db.session.commit()
        flash('User created successfully!')
        return redirect(url_for('users.users'))
    
    return render_template('users/create_user.html', form=form)


@users_bp.route('/users/<int:id>', methods=['GET'])
@login_required
def view_user(id):
    user = User.query.get_or_404(id)
    return render_template('users/view_user.html', user=user)


@users_bp.route('/users/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_user(id):
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)

    if form.validate_on_submit():
        user.branch_id = form.branch.data.id
        user.email = form.email.data
        user.name = form.name.data
        user.role = form.role.data
        
        if form.password.data:
            user.password = generate_password_hash(form.password.data, method='sha256')

        db.session.commit()
        flash('User updated successfully!')
        return redirect(url_for('users.users'))

    return render_template('users/update_user.html', form=form, user=user)


@users_bp.route('/users/delete/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    user = User.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the user. Please try again.')

    return redirect(url_for('users.users'))

