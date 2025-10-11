# auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime
from database import db, User, UserRole
from translations import get_text as _get_text

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Employee login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact administrator.', 'danger')
                return redirect(url_for('auth.login'))
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Log in user
            login_user(user, remember=remember)
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Log out current user"""
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    # Get user statistics
    total_apps = current_user.applications.count()
    active_apps = current_user.applications.filter_by(status='In-Process').count()
    approved_apps = current_user.applications.filter_by(status='Approved').count()
    declined_apps = current_user.applications.filter_by(status='Declined').count()
    
    # Calculate approval rate
    if total_apps > 0:
        approval_rate = (approved_apps / total_apps) * 100
    else:
        approval_rate = 0
    
    stats = {
        'total_applications': total_apps,
        'active_applications': active_apps,
        'approved_applications': approved_apps,
        'declined_applications': declined_apps,
        'approval_rate': round(approval_rate, 1)
    }
    
    return render_template('auth/profile.html', user=current_user, stats=stats)

@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password for current user"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate current password
        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('auth.change_password'))
        
        # Validate new password
        if len(new_password) < 6:
            flash('New password must be at least 6 characters long', 'danger')
            return redirect(url_for('auth.change_password'))
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('auth.change_password'))
        
        # Update password
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Password changed successfully', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html')

# Admin routes for user management
@auth_bp.route('/admin/users')
@login_required
def admin_users():
    """Admin page for managing users"""
    if current_user.role != UserRole.ADMIN:
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    return render_template('auth/admin_users.html', users=users)

@auth_bp.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
def admin_add_user():
    """Add a new user (admin only)"""
    if current_user.role != UserRole.ADMIN:
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        role = request.form.get('role', 'EMPLOYEE')
        department = request.form.get('department', '').strip()
        
        # Validate
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.admin_add_user'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('auth.admin_add_user'))
        
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=UserRole[role],
            department=department
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {username} created successfully', 'success')
        return redirect(url_for('auth.admin_users'))
    
    return render_template('auth/admin_add_user.html')

@auth_bp.route('/admin/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
def admin_toggle_user_status(user_id):
    """Toggle user active status (admin only)"""
    if current_user.role != UserRole.ADMIN:
        flash('You do not have permission to perform this action', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deactivating themselves
    if user.id == current_user.id:
        flash('You cannot deactivate your own account', 'danger')
        return redirect(url_for('auth.admin_users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}', 'success')
    
    return redirect(url_for('auth.admin_users'))

@auth_bp.route('/admin/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
def admin_reset_password(user_id):
    """Reset user password (admin only)"""
    if current_user.role != UserRole.ADMIN:
        flash('You do not have permission to perform this action', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password', '')
    
    if len(new_password) < 6:
        flash('Password must be at least 6 characters long', 'danger')
        return redirect(url_for('auth.admin_users'))
    
    user.set_password(new_password)
    db.session.commit()
    
    flash(f'Password for user {user.username} has been reset', 'success')
    return redirect(url_for('auth.admin_users'))