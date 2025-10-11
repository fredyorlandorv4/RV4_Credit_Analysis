#!/bin/bash

# RV4 Credit Dashboard - Application Deployment Script
# Run this script as rv4user after server setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_input() {
    echo -e "${BLUE}[INPUT]${NC} $1"
}

# Check if running as rv4user
if [ "$USER" != "rv4user" ]; then
    print_error "Please run this script as rv4user"
    exit 1
fi

echo "🚀 Starting RV4 Credit Dashboard application deployment..."

# Configuration variables
APP_DIR="/home/rv4user/apps/rv4-credit-dashboard"
BACKUP_DIR="/home/rv4user/backups"
LOG_DIR="/home/rv4user/logs"

# Function to generate random password
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

# Function to prompt for input with default
prompt_input() {
    local prompt="$1"
    local default="$2"
    local result

    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " result
        echo "${result:-$default}"
    else
        read -p "$prompt: " result
        echo "$result"
    fi
}

# Collect configuration
print_input "Please provide the following configuration details:"
echo ""

DOMAIN=$(prompt_input "Domain name (leave empty for IP access)" "")
DB_PASSWORD=$(prompt_input "MySQL password for rv4user" "$(generate_password)")
SECRET_KEY=$(prompt_input "Flask secret key" "$(generate_password)")
ADMIN_EMAIL=$(prompt_input "Admin email" "admin@rv4.com")
ADMIN_PASSWORD=$(prompt_input "Admin password" "admin123")

# Git repository configuration
echo ""
print_input "Repository configuration:"
REPO_URL=$(prompt_input "Git repository URL (or 'skip' to upload manually)" "skip")

# Clone or setup application
if [ "$REPO_URL" != "skip" ]; then
    print_status "Cloning repository..."
    if [ -d "$APP_DIR" ]; then
        print_warning "Application directory exists, backing up..."
        mv "$APP_DIR" "$APP_DIR.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    git clone "$REPO_URL" "$APP_DIR"
else
    print_warning "Skipping git clone. Please upload application files to $APP_DIR"
    print_warning "Press any key to continue once files are uploaded..."
    read -n 1 -s
    
    if [ ! -d "$APP_DIR" ]; then
        print_error "Application directory $APP_DIR not found!"
        exit 1
    fi
fi

cd "$APP_DIR"

# Create Python virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create environment file
print_status "Creating environment configuration..."
cat > .env << EOF
# Flask Configuration
SECRET_KEY=$SECRET_KEY
FLASK_ENV=production
DEBUG=False

# Database Configuration
DATABASE_URL=mysql+pymysql://rv4user:$DB_PASSWORD@localhost/rv4_credit_db
SQLALCHEMY_TRACK_MODIFICATIONS=False

# Session Configuration
REMEMBER_COOKIE_DURATION=7
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=$APP_DIR/uploads

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=$APP_DIR/logs/app.log

# Security Configuration
WTF_CSRF_ENABLED=True
WTF_CSRF_TIME_LIMIT=3600
EOF

# Create required directories
print_status "Creating application directories..."
mkdir -p logs uploads data weights application_data report
chmod 755 logs uploads data weights application_data report
touch logs/app.log
chmod 644 logs/app.log

# Setup database
print_status "Setting up database..."
mysql -u root -p << EOF
CREATE DATABASE IF NOT EXISTS rv4_credit_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'rv4user'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON rv4_credit_db.* TO 'rv4user'@'localhost';
FLUSH PRIVILEGES;
EOF

# Initialize database schema
print_status "Initializing database schema..."
python3 -c "
from app_updated import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"

# Create admin user
print_status "Creating admin user..."
python3 -c "
from app_updated import app, db
from database import User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Check if admin user exists
    existing_admin = User.query.filter_by(email='$ADMIN_EMAIL').first()
    if existing_admin:
        print('Admin user already exists')
    else:
        admin = User(
            email='$ADMIN_EMAIL',
            password_hash=generate_password_hash('$ADMIN_PASSWORD'),
            first_name='Admin',
            last_name='User',
            role='admin',
            department='IT'
        )
        db.session.add(admin)
        db.session.commit()
        print('Admin user created successfully')
"

# Create Gunicorn configuration
print_status "Creating Gunicorn configuration..."
cat > gunicorn.conf.py << EOF
# Gunicorn configuration file
bind = "127.0.0.1:8000"
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
user = "rv4user"
group = "rv4user"
tmp_upload_dir = None
logfile = "$APP_DIR/logs/gunicorn.log"
loglevel = "info"
access_logfile = "$APP_DIR/logs/access.log"
error_logfile = "$APP_DIR/logs/error.log"
EOF

# Create systemd service
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/rv4-credit-dashboard.service > /dev/null << EOF
[Unit]
Description=RV4 Credit Dashboard Gunicorn Application
After=network.target mysql.service

[Service]
Type=notify
User=rv4user
Group=rv4user
RuntimeDirectory=rv4-credit-dashboard
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/gunicorn -c gunicorn.conf.py app_updated:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
print_status "Configuring Nginx..."
if [ -n "$DOMAIN" ]; then
    SERVER_NAME="$DOMAIN www.$DOMAIN"
else
    SERVER_NAME="_"
fi

sudo tee /etc/nginx/sites-available/rv4-credit-dashboard > /dev/null << EOF
server {
    listen 80;
    server_name $SERVER_NAME;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript application/json;
    
    # Static files
    location /static {
        alias $APP_DIR/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # Uploads
    location /uploads {
        alias $APP_DIR/uploads;
        expires 1d;
        add_header Cache-Control "public";
    }
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        proxy_buffering off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # File upload size
    client_max_body_size 16M;
    
    # Logging
    access_log /var/log/nginx/rv4-access.log;
    error_log /var/log/nginx/rv4-error.log;
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/rv4-credit-dashboard /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Create backup scripts
print_status "Creating backup scripts..."

# Database backup script
cat > backup_db.sh << EOF
#!/bin/bash

BACKUP_DIR="$BACKUP_DIR"
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="rv4_credit_db_backup_\$DATE.sql"

# Create backup directory
mkdir -p \$BACKUP_DIR

# Create database backup
mysqldump -u rv4user -p'$DB_PASSWORD' rv4_credit_db > \$BACKUP_DIR/\$BACKUP_FILE

# Compress backup
gzip \$BACKUP_DIR/\$BACKUP_FILE

# Keep only last 7 days of backups
find \$BACKUP_DIR -name "rv4_credit_db_backup_*.sql.gz" -mtime +7 -delete

echo "Database backup completed: \$BACKUP_FILE.gz"
EOF

# Application backup script
cat > backup_app.sh << EOF
#!/bin/bash

BACKUP_DIR="$BACKUP_DIR"
DATE=\$(date +%Y%m%d_%H%M%S)
APP_DIR="$APP_DIR"

# Create backup directory
mkdir -p \$BACKUP_DIR

# Backup application data
tar -czf \$BACKUP_DIR/app_data_backup_\$DATE.tar.gz \\
    \$APP_DIR/data \\
    \$APP_DIR/weights \\
    \$APP_DIR/application_data \\
    \$APP_DIR/uploads \\
    \$APP_DIR/.env

# Keep only last 7 days of backups
find \$BACKUP_DIR -name "app_data_backup_*.tar.gz" -mtime +7 -delete

echo "Application data backup completed: app_data_backup_\$DATE.tar.gz"
EOF

# Make scripts executable
chmod +x backup_db.sh backup_app.sh

# Setup logrotate
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/rv4-credit-dashboard > /dev/null << EOF
$APP_DIR/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    create 644 rv4user rv4user
    postrotate
        systemctl reload rv4-credit-dashboard
    endscript
}
EOF

# Enable and start services
print_status "Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable rv4-credit-dashboard
sudo systemctl start rv4-credit-dashboard
sudo systemctl restart nginx

# Setup cron jobs for backups
print_status "Setting up automated backups..."
(crontab -l 2>/dev/null; echo "0 2 * * * $APP_DIR/backup_db.sh >> $LOG_DIR/backup.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "0 3 * * * $APP_DIR/backup_app.sh >> $LOG_DIR/backup.log 2>&1") | crontab -

# Check service status
print_status "Checking service status..."
sleep 5

if systemctl is-active --quiet rv4-credit-dashboard; then
    print_status "✅ Application service is running"
else
    print_error "❌ Application service failed to start"
    print_error "Check logs: sudo journalctl -u rv4-credit-dashboard -f"
fi

if systemctl is-active --quiet nginx; then
    print_status "✅ Nginx service is running"
else
    print_error "❌ Nginx service failed to start"
fi

# Final setup instructions
echo ""
print_status "🎉 Deployment completed successfully!"
echo ""
print_status "Configuration Summary:"
print_status "====================="
print_status "Application URL: http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_SERVER_IP')"
[ -n "$DOMAIN" ] && print_status "Domain: http://$DOMAIN"
print_status "Admin Email: $ADMIN_EMAIL"
print_status "Admin Password: $ADMIN_PASSWORD"
print_status "Database Password: $DB_PASSWORD"
echo ""

print_status "Next Steps:"
print_status "=========="
print_status "1. Access your application in a web browser"
print_status "2. Login with admin credentials"
print_status "3. Test all functionality"

if [ -n "$DOMAIN" ]; then
    print_status "4. Setup SSL certificate: sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
fi

print_status "5. Configure monitoring and alerts"
print_status "6. Test backup procedures"
echo ""

print_warning "Security Reminders:"
print_warning "=================="
print_warning "- Change default passwords immediately"
print_warning "- Configure proper firewall rules"
print_warning "- Setup monitoring and alerting"
print_warning "- Regularly update system packages"
print_warning "- Test backup and restore procedures"
echo ""

print_status "Log Locations:"
print_status "============="
print_status "Application: $APP_DIR/logs/"
print_status "Nginx: /var/log/nginx/"
print_status "System: sudo journalctl -u rv4-credit-dashboard"
