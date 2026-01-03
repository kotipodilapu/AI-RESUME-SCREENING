from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from backend.models import User, db
from backend.extensions import bcrypt

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('routes.admin_dashboard'))
        return redirect(url_for('routes.user_dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.register'))
            
        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email already exists', 'danger')
            return redirect(url_for('auth.register'))
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password)
        
        # Logic: If email starts with 'admin', automatically assign 'admin' role.
        if email.lower().startswith('admin'):
            new_user.role = 'admin'
        else:
            new_user.role = 'user'

        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created! You can now login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('routes.admin_dashboard'))
        return redirect(url_for('routes.user_dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('routes.admin_dashboard'))
            else:
                return redirect(url_for('routes.user_dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
            
    return render_template('login.html')



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
