#!/bin/bash

# RV4 Credit Dashboard - Quick Digital Ocean Deployment
# This script automates the entire deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_input() { echo -e "${BLUE}[INPUT]${NC} $1"; }

echo "🚀 RV4 Credit Dashboard - Digital Ocean Quick Deployment"
echo "========================================================="
echo ""

# Check if running on Ubuntu
if [[ ! -f /etc/lsb-release ]] || ! grep -q "Ubuntu" /etc/lsb-release; then
    print_error "This script is designed for Ubuntu. Please use Ubuntu 22.04 LTS."
    exit 1
fi

# Check if running as root initially
if [ "$EUID" -eq 0 ]; then
    print_status "Running initial setup as root..."
    SETUP_MODE="root"
elif [ "$USER" = "rv4user" ]; then
    print_status "Running application deployment as rv4user..."
    SETUP_MODE="app"
else
    print_error "Please run this script as either root (for initial setup) or rv4user (for app deployment)"
    exit 1
fi

# Function to generate random password
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

# Function to check if service is running
check_service() {
    if systemctl is-active --quiet $1; then
        print_status "✅ $1 is running"
        return 0
    else
        print_error "❌ $1 is not running"
        return 1
    fi
}

# ROOT SETUP MODE
if [ "$SETUP_MODE" = "root" ]; then
    print_status "Starting server setup..."
    
    # Update system
    print_status "Updating system packages..."
    apt update && apt upgrade -y
    
    # Install essential packages
    print_status "Installing essential packages..."
    apt install -y \
        python3 python3-pip python3-venv git nginx mysql-server redis-server \
        supervisor htop curl wget unzip fail2ban certbot python3-certbot-nginx \
        ufw logrotate software-properties-common
    
    # Install Node.js
    print_status "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y nodejs
    
    # Create application user
    print_status "Creating application user..."
    if ! id "rv4user" &>/dev/null; then
        adduser --disabled-password --gecos "" rv4user
        usermod -aG sudo rv4user
        # Copy SSH keys if they exist
        if [ -d /root/.ssh ]; then
            mkdir -p /home/rv4user/.ssh
            cp /root/.ssh/authorized_keys /home/rv4user/.ssh/ 2>/dev/null || true
            chown -R rv4user:rv4user /home/rv4user/.ssh
            chmod 700 /home/rv4user/.ssh
            chmod 600 /home/rv4user/.ssh/authorized_keys 2>/dev/null || true
        fi
    fi
    
    # Configure firewall
    print_status "Configuring firewall..."
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 'Nginx Full'
    ufw --force enable
    
    # Secure MySQL
    print_status "Securing MySQL..."
    mysql -e "DELETE FROM mysql.user WHERE User='';"
    mysql -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
    mysql -e "DROP DATABASE IF EXISTS test;"
    mysql -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';"
    mysql -e "FLUSH PRIVILEGES;"
    
    # Configure fail2ban
    print_status "Configuring fail2ban..."
    cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[nginx-http-auth]
enabled = true

[nginx-noscript]
enabled = true

[nginx-badbots]
enabled = true

[nginx-noproxy]
enabled = true
EOF
    
    # Start services
    print_status "Starting services..."
    systemctl enable nginx mysql redis-server fail2ban
    systemctl start nginx mysql redis-server fail2ban
    
    # Create directories
    su - rv4user -c "mkdir -p /home/rv4user/{apps,backups,logs}"
    
    # Set timezone
    timedatectl set-timezone UTC
    
    # Create swap if needed
    TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    if [ "$TOTAL_MEM" -lt 2048 ] && [ ! -f /swapfile ]; then
        print_status "Creating swap file..."
        fallocate -l 1G /swapfile
        chmod 600 /swapfile
        mkswap /swapfile
        swapon /swapfile
        echo '/swapfile none swap sw 0 0' >> /etc/fstab
    fi
    
    print_status "✅ Server setup completed!"
    print_status "Next: Run this script as rv4user to deploy the application"
    print_status "Command: su - rv4user -c 'curl -sSL https://raw.githubusercontent.com/yourusername/rv4-credit-dashboard/main/deployment/quick_deploy.sh | bash'"
    
    exit 0
fi

# APPLICATION DEPLOYMENT MODE
if [ "$SETUP_MODE" = "app" ]; then
    print_status "Starting application deployment..."
    
    cd /home/rv4user
    
    # Get configuration
    print_input "Configuration Setup"
    echo "Press Enter to use default values in brackets"
    echo ""
    
    read -p "Domain name (leave empty for IP access): " DOMAIN
    read -p "Admin email [admin@rv4.com]: " ADMIN_EMAIL
    ADMIN_EMAIL=${ADMIN_EMAIL:-admin@rv4.com}
    read -s -p "Admin password [admin123]: " ADMIN_PASSWORD
    echo ""
    ADMIN_PASSWORD=${ADMIN_PASSWORD:-admin123}
    read -p "Git repository URL (or 'manual' to skip): " REPO_URL
    
    # Generate secure passwords
    DB_PASSWORD=$(generate_password)
    SECRET_KEY=$(generate_password)
    
    APP_DIR="/home/rv4user/apps/rv4-credit-dashboard"
    
    # Handle repository
    if [ "$REPO_URL" != "manual" ] && [ -n "$REPO_URL" ]; then
        print_status "Cloning repository..."
        if [ -d "$APP_DIR" ]; then
            mv "$APP_DIR" "$APP_DIR.backup.$(date +%Y%m%d_%H%M%S)"
        fi
        git clone "$REPO_URL" "$APP_DIR"
    else
        print_warning "Manual deployment selected."
        print_warning "Please upload your application files to: $APP_DIR"
        read -p "Press Enter when files are uploaded..." -r
        
        if [ ! -d "$APP_DIR" ]; then
            print_error "Application directory not found!"
            exit 1
        fi
    fi
    
    cd "$APP_DIR"
    
    # Setup Python environment
    print_status "Setting up Python environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    
    # Install dependencies
    if [ -f requirements.txt ]; then
        pip install -r requirements.txt
    else
        print_status "Installing common dependencies..."
        pip install flask flask-sqlalchemy flask-login mysql-connector-python pandas scikit-learn lightgbm plotly
    fi
    pip install gunicorn
    
    # Create environment file
    print_status "Creating environment configuration..."
    cat > .env << EOF
SECRET_KEY=$SECRET_KEY
FLASK_ENV=production
DEBUG=False
DATABASE_URL=mysql+pymysql://rv4user:$DB_PASSWORD@localhost/rv4_credit_db
SQLALCHEMY_TRACK_MODIFICATIONS=False
REMEMBER_COOKIE_DURATION=7
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=$APP_DIR/uploads
LOG_LEVEL=INFO
LOG_FILE=$APP_DIR/logs/app.log
WTF_CSRF_ENABLED=True
WTF_CSRF_TIME_LIMIT=3600
EOF
    
    # Create directories
    print_status "Creating application directories..."
    mkdir -p logs uploads data weights application_data report
    chmod 755 logs uploads data weights application_data report
    touch logs/app.log
    
    # Setup database
    print_status "Setting up database..."
    sudo mysql << EOF
CREATE DATABASE IF NOT EXISTS rv4_credit_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'rv4user'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON rv4_credit_db.* TO 'rv4user'@'localhost';
FLUSH PRIVILEGES;
EOF
    
    # Initialize database (if app_updated.py exists)
    if [ -f app_updated.py ]; then
        print_status "Initializing database..."
        python3 -c "
try:
    from app_updated import app, db
    with app.app_context():
        db.create_all()
        print('Database tables created')
except Exception as e:
    print(f'Database initialization skipped: {e}')
"
        
        # Create admin user
        python3 -c "
try:
    from app_updated import app, db
    from database import User
    from werkzeug.security import generate_password_hash
    
    with app.app_context():
        existing = User.query.filter_by(email='$ADMIN_EMAIL').first()
        if not existing:
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
            print('Admin user created')
        else:
            print('Admin user already exists')
except Exception as e:
    print(f'Admin user creation skipped: {e}')
"
    fi
    
    # Create Gunicorn config
    print_status "Creating Gunicorn configuration..."
    cat > gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 2
worker_class = "sync"
timeout = 30
keepalive = 2
max_requests = 1000
preload_app = True
user = "rv4user"
group = "rv4user"
logfile = "$APP_DIR/logs/gunicorn.log"
loglevel = "info"
access_logfile = "$APP_DIR/logs/access.log"
error_logfile = "$APP_DIR/logs/error.log"
EOF
    
    # Create systemd service
    print_status "Creating systemd service..."
    sudo tee /etc/systemd/system/rv4-credit-dashboard.service > /dev/null << EOF
[Unit]
Description=RV4 Credit Dashboard
After=network.target mysql.service

[Service]
Type=notify
User=rv4user
Group=rv4user
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
    SERVER_NAME="_"
    if [ -n "$DOMAIN" ]; then
        SERVER_NAME="$DOMAIN www.$DOMAIN"
    fi
    
    sudo tee /etc/nginx/sites-available/rv4-credit-dashboard > /dev/null << EOF
server {
    listen 80;
    server_name $SERVER_NAME;
    
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    location /static {
        alias $APP_DIR/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /uploads {
        alias $APP_DIR/uploads;
        expires 1d;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    client_max_body_size 16M;
    access_log /var/log/nginx/rv4-access.log;
    error_log /var/log/nginx/rv4-error.log;
}
EOF
    
    # Enable site
    sudo ln -sf /etc/nginx/sites-available/rv4-credit-dashboard /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo nginx -t
    
    # Create backup scripts
    print_status "Creating backup scripts..."
    cat > backup_db.sh << EOF
#!/bin/bash
BACKUP_DIR="/home/rv4user/backups"
DATE=\$(date +%Y%m%d_%H%M%S)
mkdir -p \$BACKUP_DIR
mysqldump -u rv4user -p'$DB_PASSWORD' rv4_credit_db | gzip > \$BACKUP_DIR/db_backup_\$DATE.sql.gz
find \$BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete
echo "Database backup completed"
EOF
    
    cat > backup_app.sh << EOF
#!/bin/bash
BACKUP_DIR="/home/rv4user/backups"
DATE=\$(date +%Y%m%d_%H%M%S)
mkdir -p \$BACKUP_DIR
tar -czf \$BACKUP_DIR/app_backup_\$DATE.tar.gz data weights application_data uploads .env
find \$BACKUP_DIR -name "app_backup_*.tar.gz" -mtime +7 -delete
echo "Application backup completed"
EOF
    
    chmod +x backup_db.sh backup_app.sh
    
    # Setup logrotate
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
    
    # Start services
    print_status "Starting services..."
    sudo systemctl daemon-reload
    sudo systemctl enable rv4-credit-dashboard
    sudo systemctl start rv4-credit-dashboard
    sudo systemctl restart nginx
    
    # Setup cron jobs
    print_status "Setting up automated backups..."
    (crontab -l 2>/dev/null; echo "0 2 * * * $APP_DIR/backup_db.sh >> /home/rv4user/logs/backup.log 2>&1") | crontab -
    (crontab -l 2>/dev/null; echo "0 3 * * * $APP_DIR/backup_app.sh >> /home/rv4user/logs/backup.log 2>&1") | crontab -
    
    # Wait and check services
    print_status "Checking service status..."
    sleep 5
    
    ALL_GOOD=true
    check_service "rv4-credit-dashboard" || ALL_GOOD=false
    check_service "nginx" || ALL_GOOD=false
    check_service "mysql" || ALL_GOOD=false
    
    # Get server IP
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_SERVER_IP")
    
    echo ""
    if [ "$ALL_GOOD" = true ]; then
        print_status "🎉 Deployment completed successfully!"
    else
        print_warning "⚠️ Deployment completed with some issues. Check the logs above."
    fi
    
    echo ""
    print_status "🔗 Access Information:"
    print_status "====================="
    print_status "URL: http://$SERVER_IP"
    [ -n "$DOMAIN" ] && print_status "Domain: http://$DOMAIN"
    print_status "Admin Email: $ADMIN_EMAIL"
    print_status "Admin Password: $ADMIN_PASSWORD"
    echo ""
    
    print_status "📋 Next Steps:"
    print_status "=============="
    print_status "1. Visit your application URL"
    print_status "2. Login with admin credentials"
    print_status "3. Test all functionality"
    if [ -n "$DOMAIN" ]; then
        print_status "4. Setup SSL: sudo certbot --nginx -d $DOMAIN"
    fi
    print_status "5. Configure monitoring"
    echo ""
    
    print_status "🔧 Useful Commands:"
    print_status "=================="
    print_status "View logs: sudo journalctl -u rv4-credit-dashboard -f"
    print_status "Restart app: sudo systemctl restart rv4-credit-dashboard"
    print_status "Check status: sudo systemctl status rv4-credit-dashboard"
    print_status "Backup now: ./backup_db.sh && ./backup_app.sh"
    echo ""
    
    print_warning "🔒 Security Reminders:"
    print_warning "====================="
    print_warning "- Change default passwords"
    print_warning "- Setup SSL certificate"
    print_warning "- Configure monitoring"
    print_warning "- Test backup procedures"
    print_warning "- Update system regularly"
fi
