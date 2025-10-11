#!/usr/bin/env python3
"""
RV4 Credit Analysis System - Complete Setup Script
This script creates all necessary directories and files for the application
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
        'data'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def create_login_template():
    """Create the login.html template"""
    login_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - RV4 Credit Analysis System</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --primary-color: #4F46E5;
            --secondary-color: #7C3AED;
            --success-color: #10B981;
            --danger-color: #EF4444;
            --dark-bg: #111827;
            --card-bg: #1F2937;
            --text-primary: #F3F4F6;
            --text-secondary: #9CA3AF;
            --border-color: #374151;
            --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }

        .particles {
            position: absolute;
            width: 100%;
            height: 100%;
            overflow: hidden;
            z-index: -1;
        }

        .particle {
            position: absolute;
            width: 4px;
            height: 4px;
            background: rgba(79, 70, 229, 0.3);
            border-radius: 50%;
            animation: float 20s infinite linear;
        }

        @keyframes float {
            from {
                transform: translateY(100vh) translateX(0);
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            to {
                transform: translateY(-100vh) translateX(100px);
                opacity: 0;
            }
        }

        .login-container {
            width: 100%;
            max-width: 450px;
            padding: 2rem;
        }

        .login-card {
            background: rgba(31, 41, 55, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border-color);
            border-radius: 1rem;
            padding: 2.5rem;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            position: relative;
            overflow: hidden;
        }

        .login-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--gradient-primary);
        }

        .logo-container {
            text-align: center;
            margin-bottom: 2rem;
        }

        .logo {
            font-size: 3rem;
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }

        .logo-text {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-primary);
        }

        .logo-subtitle {
            color: var(--text-secondary);
            font-size: 0.875rem;
            margin-top: 0.25rem;
        }

        .form-control {
            background: rgba(17, 24, 39, 0.5);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 0.75rem 1rem;
            border-radius: 0.5rem;
            transition: all 0.3s ease;
        }

        .form-control:focus {
            background: rgba(17, 24, 39, 0.8);
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
            color: var(--text-primary);
        }

        .form-label {
            color: var(--text-secondary);
            font-weight: 500;
            margin-bottom: 0.5rem;
        }

        .btn-login {
            background: var(--gradient-primary);
            border: none;
            color: white;
            padding: 0.75rem 2rem;
            border-radius: 0.5rem;
            font-weight: 600;
            width: 100%;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .btn-login::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.2);
            transition: left 0.5s ease;
        }

        .btn-login:hover::before {
            left: 100%;
        }

        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(79, 70, 229, 0.3);
        }

        .form-check-input {
            background-color: rgba(17, 24, 39, 0.5);
            border-color: var(--border-color);
        }

        .form-check-input:checked {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
        }

        .alert {
            border: none;
            border-radius: 0.5rem;
            padding: 1rem 1.5rem;
            margin-bottom: 1rem;
        }

        .alert-danger {
            background: rgba(239, 68, 68, 0.1);
            color: var(--danger-color);
            border: 1px solid rgba(239, 68, 68, 0.2);
        }

        .alert-info {
            background: rgba(79, 70, 229, 0.1);
            color: #818CF8;
            border: 1px solid rgba(79, 70, 229, 0.2);
        }

        .demo-credentials {
            background: rgba(79, 70, 229, 0.1);
            border: 1px solid rgba(79, 70, 229, 0.2);
            border-radius: 0.5rem;
            padding: 1rem;
            margin-top: 1.5rem;
        }

        .demo-credentials h6 {
            color: var(--primary-color);
            font-size: 0.875rem;
            margin-bottom: 0.5rem;
        }

        .demo-credentials p {
            color: var(--text-secondary);
            font-size: 0.813rem;
            margin-bottom: 0.25rem;
        }

        .demo-credentials code {
            color: #818CF8;
            background: rgba(17, 24, 39, 0.5);
            padding: 0.125rem 0.25rem;
            border-radius: 0.25rem;
        }

        .input-group-text {
            background: rgba(17, 24, 39, 0.5);
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
        }

        @media (max-width: 576px) {
            .login-container {
                padding: 1rem;
            }
            
            .login-card {
                padding: 1.5rem;
            }
            
            .logo {
                font-size: 2.5rem;
            }
        }
    </style>
</head>
<body>
    <!-- Animated particles background -->
    <div class="particles">
        <script>
            for(let i = 0; i < 50; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.animationDelay = Math.random() * 20 + 's';
                particle.style.animationDuration = (15 + Math.random() * 10) + 's';
                document.querySelector('.particles').appendChild(particle);
            }
        </script>
    </div>

    <div class="login-container">
        <div class="login-card">
            <!-- Logo -->
            <div class="logo-container">
                <div class="logo">
                    <i class="bi bi-graph-up-arrow"></i>
                </div>
                <div class="logo-text">RV4 Credit Analysis</div>
                <div class="logo-subtitle">Secure Employee Portal</div>
            </div>

            <!-- Flash Messages -->
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                            {{ message }}
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <!-- Login Form -->
            <form method="POST" action="{{ url_for('auth.login') }}">
                <div class="mb-3">
                    <label class="form-label">
                        <i class="bi bi-person me-1"></i>
                        Username or Email
                    </label>
                    <div class="input-group">
                        <span class="input-group-text">
                            <i class="bi bi-person-circle"></i>
                        </span>
                        <input type="text" class="form-control" name="username" required autofocus>
                    </div>
                </div>

                <div class="mb-3">
                    <label class="form-label">
                        <i class="bi bi-lock me-1"></i>
                        Password
                    </label>
                    <div class="input-group">
                        <span class="input-group-text">
                            <i class="bi bi-key"></i>
                        </span>
                        <input type="password" class="form-control" name="password" required>
                    </div>
                </div>

                <div class="mb-4">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" name="remember" id="remember">
                        <label class="form-check-label" for="remember">
                            Remember me for 7 days
                        </label>
                    </div>
                </div>

                <button type="submit" class="btn btn-login">
                    <i class="bi bi-box-arrow-in-right me-2"></i>
                    Sign In
                </button>
            </form>

            <!-- Demo Credentials -->
            <div class="demo-credentials">
                <h6>
                    <i class="bi bi-info-circle me-1"></i>
                    Demo Credentials
                </h6>
                <p>Admin: <code>admin</code> / <code>admin123</code></p>
                <p>Employee: <code>employee1</code> / <code>password123</code></p>
            </div>
        </div>

        <!-- Copyright -->
        <div class="text-center mt-4">
            <p class="text-secondary small">
                © 2025 RV4 Credit Analysis System. All rights reserved.
            </p>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''
    
    with open('templates/auth/login.html', 'w', encoding='utf-8') as f:
        f.write(login_html)
    print("✓ Created templates/auth/login.html")

def create_base_updated_template():
    """Create an updated base.html template that works with login"""
    base_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ get_text('dashboard_title') if get_text else 'RV4 Credit Analysis' }}{% endblock %}</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <!-- Plotly -->
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    
    <style>
        :root {
            --primary-color: #4F46E5;
            --secondary-color: #7C3AED;
            --success-color: #10B981;
            --danger-color: #EF4444;
            --warning-color: #F59E0B;
            --dark-bg: #111827;
            --card-bg: #1F2937;
            --text-primary: #F3F4F6;
            --text-secondary: #9CA3AF;
            --border-color: #374151;
            --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--dark-bg);
            color: var(--text-primary);
            overflow-x: hidden;
            min-height: 100vh;
        }

        /* Animated Background */
        .animated-bg {
            position: fixed;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            z-index: -1;
            background: linear-gradient(45deg, #0F172A 0%, #1E293B 50%, #0F172A 100%);
            overflow: hidden;
        }

        .animated-bg::before {
            content: '';
            position: absolute;
            width: 150%;
            height: 150%;
            background: radial-gradient(circle at 20% 80%, rgba(79, 70, 229, 0.1) 0%, transparent 50%),
                        radial-gradient(circle at 80% 20%, rgba(124, 58, 237, 0.1) 0%, transparent 50%),
                        radial-gradient(circle at 40% 40%, rgba(16, 185, 129, 0.05) 0%, transparent 50%);
            animation: bgAnimation 20s ease-in-out infinite;
        }

        @keyframes bgAnimation {
            0%, 100% { transform: translate(0, 0) rotate(0deg); }
            33% { transform: translate(-5%, -5%) rotate(1deg); }
            66% { transform: translate(5%, -5%) rotate(-1deg); }
        }

        /* Navigation */
        .navbar {
            background: rgba(31, 41, 55, 0.8);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border-color);
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 1000;
        }

        .navbar-brand {
            font-weight: 700;
            font-size: 1.5rem;
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-decoration: none;
        }

        .nav-link {
            color: var(--text-secondary);
            font-weight: 500;
            padding: 0.5rem 1rem;
            margin: 0 0.25rem;
            border-radius: 0.5rem;
            transition: all 0.3s ease;
            text-decoration: none;
        }

        .nav-link:hover, .nav-link.active {
            color: var(--text-primary);
            background: rgba(79, 70, 229, 0.1);
        }

        /* Language Switcher */
        .language-switcher {
            background: rgba(79, 70, 229, 0.1);
            border: 1px solid rgba(79, 70, 229, 0.3);
            border-radius: 2rem;
            padding: 0.25rem;
            display: flex;
            gap: 0.25rem;
        }

        .lang-btn {
            padding: 0.5rem 1rem;
            border: none;
            background: transparent;
            color: var(--text-secondary);
            border-radius: 1.5rem;
            font-weight: 500;
            transition: all 0.3s ease;
            cursor: pointer;
            text-decoration: none;
        }

        .lang-btn.active {
            background: var(--gradient-primary);
            color: white;
        }

        /* Cards */
        .dashboard-card {
            background: rgba(31, 41, 55, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border-color);
            border-radius: 1rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .dashboard-card:hover {
            transform: translateY(-2px);
            border-color: rgba(79, 70, 229, 0.3);
            box-shadow: 0 10px 30px rgba(79, 70, 229, 0.2);
        }

        /* Buttons */
        .btn-primary-gradient {
            background: var(--gradient-primary);
            border: none;
            color: white;
            padding: 0.75rem 2rem;
            border-radius: 0.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .btn-primary-gradient:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(79, 70, 229, 0.3);
        }

        /* Form Elements */
        .form-control, .form-select {
            background: rgba(31, 41, 55, 0.8);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 0.75rem 1rem;
            border-radius: 0.5rem;
        }

        .form-control:focus, .form-select:focus {
            background: rgba(31, 41, 55, 1);
            border-color: rgba(79, 70, 229, 0.5);
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
            color: var(--text-primary);
        }

        /* Logout Button */
        .btn-logout {
            background: rgba(239, 68, 68, 0.1);
            color: var(--danger-color);
            border: 1px solid rgba(239, 68, 68, 0.3);
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            transition: all 0.3s ease;
        }

        .btn-logout:hover {
            background: rgba(239, 68, 68, 0.2);
            color: #FF6B6B;
        }
    </style>
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Animated Background -->
    <div class="animated-bg"></div>

    <!-- Navigation -->
    <nav class="navbar">
        <div class="container-fluid">
            <a class="navbar-brand" href="{{ url_for('dashboard') if current_user.is_authenticated else '#' }}">
                <i class="bi bi-graph-up-arrow me-2"></i>
                RV4 Credit Analysis
            </a>
            
            <div class="d-flex align-items-center ms-auto">
                {% if current_user.is_authenticated %}
                <div class="nav-links d-none d-md-flex me-4">
                    <a href="{{ url_for('dashboard') }}" class="nav-link {% if request.endpoint == 'dashboard' %}active{% endif %}">
                        <i class="bi bi-grid-3x3-gap me-1"></i>
                        Dashboard
                    </a>
                    <a href="{{ url_for('my_clients') }}" class="nav-link {% if request.endpoint == 'my_clients' %}active{% endif %}">
                        <i class="bi bi-people me-1"></i>
                        My Clients
                    </a>
                    <a href="{{ url_for('predictions') }}" class="nav-link {% if request.endpoint == 'predictions' %}active{% endif %}">
                        <i class="bi bi-cpu me-1"></i>
                        Predictions
                    </a>
                </div>
                
                <div class="dropdown me-3">
                    <button class="btn btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                        <i class="bi bi-person-circle me-1"></i>
                        {{ current_user.first_name }}
                    </button>
                    <ul class="dropdown-menu dropdown-menu-dark">
                        <li><a class="dropdown-item" href="{{ url_for('auth.profile') }}">
                            <i class="bi bi-person me-2"></i>Profile
                        </a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item" href="{{ url_for('auth.logout') }}">
                            <i class="bi bi-box-arrow-right me-2"></i>Logout
                        </a></li>
                    </ul>
                </div>
                {% endif %}
                
                <div class="language-switcher">
                    <a href="{{ url_for('change_language', lang='en') }}" class="lang-btn {% if session.get('language', 'en') == 'en' %}active{% endif %}">EN</a>
                    <a href="{{ url_for('change_language', lang='es') }}" class="lang-btn {% if session.get('language', 'en') == 'es' %}active{% endif %}">ES</a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Flash Messages -->
    <div class="container-fluid px-4 pt-3">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>

    <!-- Main Content -->
    <main class="container-fluid px-4 py-4">
        {% block content %}{% endblock %}
    </main>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>'''
    
    with open('templates/base.html', 'w', encoding='utf-8') as f:
        f.write(base_html)
    print("✓ Updated templates/base.html")

def main():
    print("\n" + "="*60)
    print("RV4 Credit Analysis System - Setup Script")
    print("="*60 + "\n")
    
    # Create directory structure
    print("Creating directory structure...")
    create_directory_structure()
    
    # Create template files
    print("\nCreating template files...")
    create_login_template()
    create_base_updated_template()
    
    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Ensure you have all the Python files:")
    print("   - app_updated.py")
    print("   - database.py")
    print("   - auth.py")
    print("   - model_pipeline.py")
    print("   - plotting.py")
    print("   - translations.py")
    print("   - sample_data.py")
    print("\n2. Install required packages:")
    print("   pip install -r requirements.txt")
    print("\n3. Configure your MySQL database connection in app_updated.py")
    print("\n4. Run the application:")
    print("   python app_updated.py")
    print("\nDefault login credentials:")
    print("   Admin: admin / admin123")
    print("   Employee: employee1 / password123")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()