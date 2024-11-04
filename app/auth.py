from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
from passlib.hash import sha256_crypt
from . import db 
from app.forms import *
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
def index():
    
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('error Invalid login details.')
            return redirect(url_for('auth.login'))
        if sha256_crypt.verify(password, user.password):
            login_user(user)
            session['userid'] = user.id
            return redirect(url_for('dashboard.dashboard'))

        flash('error Invalid login details.')
        return redirect(url_for('auth.login'))

    return render_template('login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        passwordata = sha256_crypt.encrypt(password)

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Error email already exists!')
            return redirect(url_for('auth.register'))
        new_user = User(email=email, password=passwordata, name=name, role=1)
        db.session.add(new_user)
        db.session.commit()

        flash('Successfully registered new user!')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)


@auth_bp.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    g=None
    return redirect(url_for('auth.index'))