#!/usr/bin/env python3
"""
RV4 Credit Analysis System - Complete Setup Script
This script creates ALL necessary directories and template files
"""

import os
import sys

def create_directory_structure():
    """Create the complete directory structure"""
    directories = [
        'templates',
        'templates/auth',
        'static',
        'static/css',
        'static/js',
        'data'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def create_admin_users_template():
    """Create admin users management template"""
    content = '''{% extends "base.html" %}

{% block title %}User Management - Admin{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center">
            <div>
                <h1 class="display-6 fw-bold mb-2">
                    <i class="bi bi-shield-lock me-2"></i>
                    User Management
                </h1>
                <p class="text-secondary">Manage system users and permissions</p>
            </div>
            <button class="btn btn-primary-gradient" data-bs-toggle="modal" data-bs-target="#addUserModal">
                <i class="bi bi-person-plus me-2"></i>
                Add New User
            </button>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="dashboard-card">
            <div class="table-responsive">
                <table class="table table-dark table-hover">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Username</th>
                            <th>Full Name</th>
                            <th>Email</th>
                            <th>Role</th>
                            <th>Department</th>
                            <th>Status</th>
                            <th>Last Login</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for user in users %}
                        <tr>
                            <td>{{ user.id }}</td>
                            <td>{{ user.username }}</td>
                            <td>{{ user.get_full_name() }}</td>
                            <td>{{ user.email }}</td>
                            <td>
                                <span class="badge bg-primary">{{ user.role.value|title }}</span>
                            </td>
                            <td>{{ user.department or '-' }}</td>
                            <td>
                                {% if user.is_active %}
                                <span class="badge bg-success">Active</span>
                                {% else %}
                                <span class="badge bg-danger">Inactive</span>
                                {% endif %}
                            </td>
                            <td>{{ user.last_login.strftime('%Y-%m-%d') if user.last_login else 'Never' }}</td>
                            <td>
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-outline-warning" onclick="editUser({{ user.id }})">
                                        <i class="bi bi-pencil"></i>
                                    </button>
                                    <button class="btn btn-outline-info" onclick="resetPassword({{ user.id }})">
                                        <i class="bi bi-key"></i>
                                    </button>
                                    {% if user.id != current_user.id %}
                                    <form method="POST" action="{{ url_for('auth.admin_toggle_user_status', user_id=user.id) }}" style="display: inline;">
                                        <button type="submit" class="btn btn-outline-danger">
                                            <i class="bi bi-power"></i>
                                        </button>
                                    </form>
                                    {% endif %}
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<!-- Add User Modal -->
<div class="modal fade" id="addUserModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Add New User</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form method="POST" action="{{ url_for('auth.admin_add_user') }}">
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">Username</label>
                        <input type="text" class="form-control" name="username" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Email</label>
                        <input type="email" class="form-control" name="email" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Password</label>
                        <input type="password" class="form-control" name="password" required>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">First Name</label>
                            <input type="text" class="form-control" name="first_name" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Last Name</label>
                            <input type="text" class="form-control" name="last_name" required>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Role</label>
                        <select class="form-select" name="role" required>
                            <option value="EMPLOYEE">Employee</option>
                            <option value="MANAGER">Manager</option>
                            <option value="ADMIN">Admin</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Department</label>
                        <input type="text" class="form-control" name="department">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Create User</button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}'''
    
    with open('templates/auth/admin_users.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ Created templates/auth/admin_users.html")

def create_change_password_template():
    """Create change password template"""
    content = '''{% extends "base.html" %}

{% block title %}Change Password{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-6">
        <div class="dashboard-card">
            <h3 class="mb-4">
                <i class="bi bi-key me-2"></i>
                Change Password
            </h3>
            
            <form method="POST" action="{{ url_for('auth.change_password') }}">
                <div class="mb-3">
                    <label class="form-label">Current Password</label>
                    <input type="password" class="form-control" name="current_password" required>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">New Password</label>
                    <input type="password" class="form-control" name="new_password" required minlength="6">
                    <div class="form-text">Password must be at least 6 characters long</div>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">Confirm New Password</label>
                    <input type="password" class="form-control" name="confirm_password" required>
                </div>
                
                <div class="d-flex justify-content-between">
                    <a href="{{ url_for('auth.profile') }}" class="btn btn-outline-secondary">
                        <i class="bi bi-arrow-left me-2"></i>
                        Back to Profile
                    </a>
                    <button type="submit" class="btn btn-primary-gradient">
                        <i class="bi bi-check-circle me-2"></i>
                        Update Password
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}'''
    
    with open('templates/auth/change_password.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ Created templates/auth/change_password.html")

def create_admin_add_user_template():
    """Create admin add user template"""
    content = '''{% extends "base.html" %}

{% block title %}Add New User - Admin{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="dashboard-card">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h3 class="mb-0">
                    <i class="bi bi-person-plus me-2"></i>
                    Add New User
                </h3>
                <a href="{{ url_for('auth.admin_users') }}" class="btn btn-outline-secondary">
                    <i class="bi bi-arrow-left me-2"></i>
                    Back to Users
                </a>
            </div>
            
            <form method="POST" action="{{ url_for('auth.admin_add_user') }}">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Username <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" name="username" required>
                    </div>
                    
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Email <span class="text-danger">*</span></label>
                        <input type="email" class="form-control" name="email" required>
                    </div>
                    
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Password <span class="text-danger">*</span></label>
                        <input type="password" class="form-control" name="password" required minlength="6">
                        <div class="form-text">Minimum 6 characters</div>
                    </div>
                    
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Confirm Password <span class="text-danger">*</span></label>
                        <input type="password" class="form-control" name="confirm_password" required>
                    </div>
                    
                    <div class="col-md-6 mb-3">
                        <label class="form-label">First Name <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" name="first_name" required>
                    </div>
                    
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Last Name <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" name="last_name" required>
                    </div>
                    
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Role <span class="text-danger">*</span></label>
                        <select class="form-select" name="role" required>
                            <option value="EMPLOYEE" selected>Employee</option>
                            <option value="MANAGER">Manager</option>
                            <option value="ADMIN">Admin</option>
                        </select>
                    </div>
                    
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Department</label>
                        <input type="text" class="form-control" name="department" placeholder="e.g., Credit Analysis">
                    </div>
                </div>
                
                <div class="d-flex justify-content-end gap-2">
                    <button type="reset" class="btn btn-outline-secondary">
                        <i class="bi bi-x-circle me-2"></i>
                        Clear
                    </button>
                    <button type="submit" class="btn btn-primary-gradient">
                        <i class="bi bi-check-circle me-2"></i>
                        Create User
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}'''
    
    with open('templates/auth/admin_add_user.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ Created templates/auth/admin_add_user.html")

def update_translations():
    """Update translations.py with missing keys"""
    additional_translations = '''
# Add these to your existing TRANSLATIONS dictionary in translations.py

# Navigation and general
'dashboard': 'Dashboard',
'my_clients': 'My Clients',
'new_application': 'New Application',
'predictions': 'Predictions',
'risk_analysis': 'Risk Analysis',
'admin': 'Admin',
'profile': 'Profile',
'logout': 'Logout',
'change_password': 'Change Password',

# For Spanish
'dashboard': 'Tablero',
'my_clients': 'Mis Clientes',
'new_application': 'Nueva Solicitud',
'predictions': 'Predicciones',
'risk_analysis': 'Análisis de Riesgo',
'admin': 'Administrador',
'profile': 'Perfil',
'logout': 'Cerrar Sesión',
'change_password': 'Cambiar Contraseña',
'''
    print("\n📝 Additional translations to add to translations.py:")
    print(additional_translations)

def main():
    print("\n" + "="*60)
    print("RV4 Credit Analysis System - Complete Setup Script")
    print("="*60 + "\n")
    
    # Create directory structure
    print("Creating directory structure...")
    create_directory_structure()
    
    # Create all template files
    print("\nCreating template files...")
    
    # Check if templates/auth directory exists
    if not os.path.exists('templates/auth'):
        os.makedirs('templates/auth', exist_ok=True)
    
    # Create auth templates
    create_admin_users_template()
    create_change_password_template()
    create_admin_add_user_template()
    
    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    
    print("\n📋 Created Files:")
    print("  ✓ templates/auth/admin_users.html")
    print("  ✓ templates/auth/change_password.html")
    print("  ✓ templates/auth/admin_add_user.html")
    
    print("\n📋 Required Templates (from artifacts):")
    print("  • templates/base.html (Updated version)")
    print("  • templates/auth/login.html")
    print("  • templates/auth/profile.html")
    print("  • templates/dashboard.html")
    print("  • templates/my_clients.html")
    print("  • templates/client_detail.html")
    print("  • templates/new_application.html")
    print("  • templates/predictions.html")
    print("  • templates/withdrawal_prediction.html")
    print("  • templates/completeness.html")
    
    print("\n⚠️ Important Notes:")
    print("1. Save all the artifact templates to their respective files")
    print("2. Update your database connection in app_updated.py")
    print("3. Ensure MySQL is running")
    print("4. Install all required packages:")
    print("   pip install flask flask-sqlalchemy flask-login pymysql")
    print("   pip install pandas plotly scikit-learn numpy lightgbm")
    
    print("\n🚀 To run the application:")
    print("   python app_updated.py")
    
    print("\n🔐 Default Credentials:")
    print("   Admin: admin / admin123")
    print("   Employee: employee1 / password123")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()