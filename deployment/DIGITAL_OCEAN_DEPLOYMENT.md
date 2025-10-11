# RV4 Credit Dashboard - Digital Ocean Ubuntu Server Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Digital Ocean Droplet Setup](#digital-ocean-droplet-setup)
3. [Server Initial Configuration](#server-initial-configuration)
4. [Application Deployment](#application-deployment)
5. [Database Setup](#database-setup)
6. [Web Server Configuration](#web-server-configuration)
7. [SSL Certificate Setup](#ssl-certificate-setup)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Backup Strategy](#backup-strategy)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### Local Requirements
- Digital Ocean account with payment method
- SSH key pair generated
- Domain name (optional but recommended)
- Git repository access

### Recommended Droplet Specifications
- **Development**: 1GB RAM, 1 vCPU, 25GB SSD ($6/month)
- **Production**: 2GB RAM, 1 vCPU, 50GB SSD ($12/month)
- **High Traffic**: 4GB RAM, 2 vCPUs, 80GB SSD ($24/month)

## Digital Ocean Droplet Setup

### 1. Create SSH Key Pair (if not exists)
```bash
# On your local machine
ssh-keygen -t rsa -b 4096 -c "your-email@example.com"
# Save as: ~/.ssh/rv4_digital_ocean
```

### 2. Create Droplet
1. Log into Digital Ocean Dashboard
2. Click "Create" → "Droplets"
3. **Choose Image**: Ubuntu 22.04 (LTS) x64
4. **Choose Size**: Select based on your needs (minimum 1GB RAM)
5. **Choose Datacenter**: Select closest to your users
6. **Authentication**: Add your SSH key
7. **Hostname**: `rv4-credit-dashboard`
8. **Tags**: `rv4`, `production`, `flask-app`

### 3. Configure Firewall (Recommended)
```bash
# Create firewall rules in DO dashboard
- SSH (22): Your IP address
- HTTP (80): All IPv4, All IPv6
- HTTPS (443): All IPv4, All IPv6
- MySQL (3306): Internal (if using managed database)
```

## Server Initial Configuration

### 1. Connect to Server
```bash
# Connect to your droplet
ssh -i ~/.ssh/rv4_digital_ocean root@YOUR_DROPLET_IP

# Update system packages
apt update && apt upgrade -y
```

### 2. Create Non-Root User
```bash
# Create application user
adduser rv4user
usermod -aG sudo rv4user

# Setup SSH access for new user
mkdir -p /home/rv4user/.ssh
cp ~/.ssh/authorized_keys /home/rv4user/.ssh/
chown -R rv4user:rv4user /home/rv4user/.ssh
chmod 700 /home/rv4user/.ssh
chmod 600 /home/rv4user/.ssh/authorized_keys

# Test SSH access with new user
ssh -i ~/.ssh/rv4_digital_ocean rv4user@YOUR_DROPLET_IP
```

### 3. Configure Firewall (UFW)
```bash
# Enable UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

### 4. Install Essential Packages
```bash
# Update package list
sudo apt update

# Install essential packages
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    nginx \
    mysql-server \
    redis-server \
    supervisor \
    htop \
    curl \
    wget \
    unzip \
    fail2ban \
    certbot \
    python3-certbot-nginx

# Install Node.js (for potential frontend tools)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

## Application Deployment

### 1. Clone Repository
```bash
# Switch to application user
sudo su - rv4user

# Create application directory
mkdir -p /home/rv4user/apps
cd /home/rv4user/apps

# Clone repository
git clone https://github.com/yourusername/rv4-credit-dashboard.git
cd rv4-credit-dashboard

# Or upload files via SCP if private repo
# scp -r -i ~/.ssh/rv4_digital_ocean ./rv4-credit-dashboard rv4user@YOUR_DROPLET_IP:~/apps/
```

### 2. Setup Python Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install application dependencies
pip install -r requirements.txt

# Install additional production dependencies
pip install gunicorn
```

### 3. Configure Environment Variables
```bash
# Create environment file
nano /home/rv4user/apps/rv4-credit-dashboard/.env
```

Add the following content to `.env`:
```bash
# Flask Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_ENV=production
DEBUG=False

# Database Configuration
DATABASE_URL=mysql+pymysql://rv4user:secure_password@localhost/rv4_credit_db
SQLALCHEMY_TRACK_MODIFICATIONS=False

# Session Configuration
REMEMBER_COOKIE_DURATION=7
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216  # 16MB
UPLOAD_FOLDER=/home/rv4user/apps/rv4-credit-dashboard/uploads

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/home/rv4user/apps/rv4-credit-dashboard/logs/app.log

# Security Configuration
WTF_CSRF_ENABLED=True
WTF_CSRF_TIME_LIMIT=3600
```

### 4. Create Directory Structure
```bash
# Create required directories
mkdir -p logs uploads data weights application_data report
chmod 755 logs uploads data weights application_data report

# Create log file
touch logs/app.log
chmod 644 logs/app.log
```

## Database Setup

### 1. Secure MySQL Installation
```bash
sudo mysql_secure_installation
```
Follow prompts:
- Remove anonymous users: Yes
- Disallow root login remotely: Yes
- Remove test database: Yes
- Reload privilege tables: Yes

### 2. Create Application Database
```bash
# Login to MySQL as root
sudo mysql -u root -p

# Create database and user
CREATE DATABASE rv4_credit_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'rv4user'@'localhost' IDENTIFIED BY 'secure_password_change_this';
GRANT ALL PRIVILEGES ON rv4_credit_db.* TO 'rv4user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Initialize Database Schema
```bash
# Activate virtual environment
cd /home/rv4user/apps/rv4-credit-dashboard
source venv/bin/activate

# Initialize database
python3 -c "
from app_updated import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"

# Create admin user
python3 -c "
from app_updated import app, db
from database import User
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = User(
        email='admin@rv4.com',
        password_hash=generate_password_hash('admin123'),
        first_name='Admin',
        last_name='User',
        role='admin',
        department='IT'
    )
    db.session.add(admin)
    db.session.commit()
    print('Admin user created: admin@rv4.com / admin123')
"
```

## Web Server Configuration

### 1. Create Gunicorn Configuration
```bash
# Create gunicorn config
nano /home/rv4user/apps/rv4-credit-dashboard/gunicorn.conf.py
```

Add configuration:
```python
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
logfile = "/home/rv4user/apps/rv4-credit-dashboard/logs/gunicorn.log"
loglevel = "info"
access_logfile = "/home/rv4user/apps/rv4-credit-dashboard/logs/access.log"
error_logfile = "/home/rv4user/apps/rv4-credit-dashboard/logs/error.log"
```

### 2. Create Systemd Service
```bash
# Create systemd service file
sudo nano /etc/systemd/system/rv4-credit-dashboard.service
```

Add service configuration:
```ini
[Unit]
Description=RV4 Credit Dashboard Gunicorn Application
After=network.target mysql.service

[Service]
Type=notify
User=rv4user
Group=rv4user
RuntimeDirectory=rv4-credit-dashboard
WorkingDirectory=/home/rv4user/apps/rv4-credit-dashboard
Environment=PATH=/home/rv4user/apps/rv4-credit-dashboard/venv/bin
EnvironmentFile=/home/rv4user/apps/rv4-credit-dashboard/.env
ExecStart=/home/rv4user/apps/rv4-credit-dashboard/venv/bin/gunicorn -c gunicorn.conf.py app_updated:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 3. Configure Nginx
```bash
# Create Nginx site configuration
sudo nano /etc/nginx/sites-available/rv4-credit-dashboard
```

Add Nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com YOUR_DROPLET_IP;
    
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
        alias /home/rv4user/apps/rv4-credit-dashboard/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # Uploads
    location /uploads {
        alias /home/rv4user/apps/rv4-credit-dashboard/uploads;
        expires 1d;
        add_header Cache-Control "public";
    }
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
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
```

### 4. Enable and Start Services
```bash
# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/rv4-credit-dashboard /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Enable and start services
sudo systemctl enable rv4-credit-dashboard
sudo systemctl enable nginx
sudo systemctl enable mysql
sudo systemctl enable redis-server

# Start services
sudo systemctl start rv4-credit-dashboard
sudo systemctl start nginx
sudo systemctl restart mysql
sudo systemctl start redis-server

# Check service status
sudo systemctl status rv4-credit-dashboard
sudo systemctl status nginx
```

## SSL Certificate Setup

### 1. Install SSL Certificate with Let's Encrypt
```bash
# Install certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test automatic renewal
sudo certbot renew --dry-run

# Setup automatic renewal
sudo crontab -e
# Add this line:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. Update Nginx for HTTPS (if using domain)
The certbot command will automatically update your Nginx configuration for HTTPS.

## Monitoring and Logging

### 1. Setup Log Rotation
```bash
# Create logrotate configuration
sudo nano /etc/logrotate.d/rv4-credit-dashboard
```

Add logrotate configuration:
```
/home/rv4user/apps/rv4-credit-dashboard/logs/*.log {
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
```

### 2. Setup System Monitoring
```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Create monitoring script
nano /home/rv4user/monitor.sh
```

Add monitoring script:
```bash
#!/bin/bash

echo "=== System Status ==="
date
echo ""

echo "=== Memory Usage ==="
free -h
echo ""

echo "=== Disk Usage ==="
df -h
echo ""

echo "=== CPU Usage ==="
top -bn1 | grep "Cpu(s)"
echo ""

echo "=== Service Status ==="
systemctl is-active rv4-credit-dashboard
systemctl is-active nginx
systemctl is-active mysql
echo ""

echo "=== Recent Errors ==="
tail -10 /home/rv4user/apps/rv4-credit-dashboard/logs/error.log
```

Make executable:
```bash
chmod +x /home/rv4user/monitor.sh
```

### 3. Setup Fail2Ban for Security
```bash
# Configure fail2ban for Nginx
sudo nano /etc/fail2ban/jail.local
```

Add configuration:
```ini
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
```

Start fail2ban:
```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## Backup Strategy

### 1. Database Backup Script
```bash
# Create backup script
nano /home/rv4user/backup_db.sh
```

Add backup script:
```bash
#!/bin/bash

BACKUP_DIR="/home/rv4user/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="rv4_credit_db_backup_$DATE.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create database backup
mysqldump -u rv4user -p'secure_password_change_this' rv4_credit_db > $BACKUP_DIR/$BACKUP_FILE

# Compress backup
gzip $BACKUP_DIR/$BACKUP_FILE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "rv4_credit_db_backup_*.sql.gz" -mtime +7 -delete

echo "Database backup completed: $BACKUP_FILE.gz"
```

### 2. Application Backup Script
```bash
# Create application backup script
nano /home/rv4user/backup_app.sh
```

Add application backup script:
```bash
#!/bin/bash

BACKUP_DIR="/home/rv4user/backups"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/home/rv4user/apps/rv4-credit-dashboard"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup application data
tar -czf $BACKUP_DIR/app_data_backup_$DATE.tar.gz \
    $APP_DIR/data \
    $APP_DIR/weights \
    $APP_DIR/application_data \
    $APP_DIR/uploads \
    $APP_DIR/.env

# Keep only last 7 days of backups
find $BACKUP_DIR -name "app_data_backup_*.tar.gz" -mtime +7 -delete

echo "Application data backup completed: app_data_backup_$DATE.tar.gz"
```

### 3. Setup Automated Backups
```bash
# Make scripts executable
chmod +x /home/rv4user/backup_db.sh
chmod +x /home/rv4user/backup_app.sh

# Setup cron jobs
crontab -e

# Add these lines:
# Daily database backup at 2 AM
0 2 * * * /home/rv4user/backup_db.sh >> /home/rv4user/logs/backup.log 2>&1

# Daily application backup at 3 AM
0 3 * * * /home/rv4user/backup_app.sh >> /home/rv4user/logs/backup.log 2>&1
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Application Won't Start
```bash
# Check service status
sudo systemctl status rv4-credit-dashboard

# Check logs
sudo journalctl -u rv4-credit-dashboard -f

# Check application logs
tail -f /home/rv4user/apps/rv4-credit-dashboard/logs/error.log
```

#### 2. Database Connection Issues
```bash
# Test database connection
mysql -u rv4user -p rv4_credit_db

# Check MySQL status
sudo systemctl status mysql

# Check MySQL error logs
sudo tail -f /var/log/mysql/error.log
```

#### 3. Nginx Configuration Issues
```bash
# Test Nginx configuration
sudo nginx -t

# Check Nginx status
sudo systemctl status nginx

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

#### 4. High Memory Usage
```bash
# Check memory usage
free -h
htop

# Restart application if needed
sudo systemctl restart rv4-credit-dashboard
```

#### 5. SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate manually
sudo certbot renew

# Check Nginx SSL configuration
sudo nginx -t
```

### Performance Optimization

#### 1. Database Optimization
```sql
-- Add indexes for better performance
USE rv4_credit_db;
CREATE INDEX idx_applications_agent_id ON applications(agent_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_date ON applications(application_date);
CREATE INDEX idx_activity_logs_application_id ON activity_logs(application_id);
CREATE INDEX idx_activity_logs_user_id ON activity_logs(user_id);
```

#### 2. Nginx Optimization
```nginx
# Add to nginx.conf main context
worker_processes auto;
worker_connections 1024;

# Add to http context
keepalive_timeout 65;
keepalive_requests 100;
sendfile on;
tcp_nopush on;
tcp_nodelay on;
```

### Security Checklist

- ✅ Non-root user created
- ✅ SSH key authentication
- ✅ Firewall configured (UFW)
- ✅ Fail2Ban installed
- ✅ SSL certificate installed
- ✅ Database secured
- ✅ Application environment variables secured
- ✅ Log rotation configured
- ✅ Regular backups scheduled
- ✅ Monitoring in place

## Deployment Checklist

### Pre-Deployment
- [ ] Domain name configured (if applicable)
- [ ] SSH key pair generated
- [ ] Digital Ocean account ready
- [ ] Application code reviewed and tested

### Deployment Steps
- [ ] Droplet created and configured
- [ ] Server secured and updated
- [ ] Application deployed
- [ ] Database setup completed
- [ ] Web server configured
- [ ] SSL certificate installed
- [ ] Monitoring setup completed
- [ ] Backup strategy implemented

### Post-Deployment
- [ ] Application accessible via browser
- [ ] Admin user login tested
- [ ] SSL certificate working
- [ ] Monitoring alerts configured
- [ ] Backup scripts tested
- [ ] Performance optimizations applied

---

**Last Updated**: September 11, 2025  
**Version**: 1.0.0  
**Environment**: Ubuntu 22.04 LTS on Digital Ocean
