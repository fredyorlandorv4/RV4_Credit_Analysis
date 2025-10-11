# Digital Ocean Deployment Files

This directory contains all the necessary files and scripts for deploying the RV4 Credit Dashboard on Digital Ocean Ubuntu servers.

## 📁 Files Overview

### 🚀 Quick Deployment
- **`quick_deploy.sh`** - One-script deployment for both server setup and application deployment
- **`server_setup.sh`** - Initial server configuration and security setup
- **`deploy_app.sh`** - Application-specific deployment script

### 📖 Documentation
- **`DIGITAL_OCEAN_DEPLOYMENT.md`** - Complete step-by-step deployment guide
- **`DOCKER_DEPLOYMENT.md`** - Docker-based deployment instructions

## 🎯 Quick Start

### Option 1: One-Script Deployment (Recommended)
```bash
# On fresh Ubuntu 22.04 droplet as root
curl -sSL https://raw.githubusercontent.com/yourusername/rv4-credit-dashboard/main/deployment/quick_deploy.sh | bash

# Then as rv4user for application deployment
su - rv4user
curl -sSL https://raw.githubusercontent.com/yourusername/rv4-credit-dashboard/main/deployment/quick_deploy.sh | bash
```

### Option 2: Step-by-Step Deployment
```bash
# 1. Server setup (as root)
curl -sSL https://raw.githubusercontent.com/yourusername/rv4-credit-dashboard/main/deployment/server_setup.sh | bash

# 2. Application deployment (as rv4user)
curl -sSL https://raw.githubusercontent.com/yourusername/rv4-credit-dashboard/main/deployment/deploy_app.sh | bash
```

### Option 3: Docker Deployment
```bash
# Clone repository
git clone https://github.com/yourusername/rv4-credit-dashboard.git
cd rv4-credit-dashboard

# Deploy with Docker Compose
docker-compose up -d
```

## 📋 Prerequisites

### Digital Ocean Account Setup
1. **Create Digital Ocean account** with payment method
2. **Generate SSH key pair** for secure access
3. **Optional**: Register domain name for SSL certificate

### Recommended Droplet Specifications
- **Development**: 1GB RAM, 1 vCPU, 25GB SSD ($6/month)
- **Production**: 2GB RAM, 1 vCPU, 50GB SSD ($12/month)
- **High Traffic**: 4GB RAM, 2 vCPUs, 80GB SSD ($24/month)

## 🔧 Manual File Upload

If you prefer to upload files manually instead of using git:

```bash
# From your local machine
scp -r -i ~/.ssh/your_key ./rv4-credit-dashboard rv4user@YOUR_SERVER_IP:~/apps/

# Or use rsync for better performance
rsync -avz -e "ssh -i ~/.ssh/your_key" ./rv4-credit-dashboard/ rv4user@YOUR_SERVER_IP:~/apps/rv4-credit-dashboard/
```

## 🔒 Security Features Included

### Server Security
- ✅ UFW firewall configured
- ✅ Fail2Ban intrusion prevention
- ✅ Non-root user with sudo access
- ✅ SSH key authentication
- ✅ System package updates
- ✅ Security headers in Nginx

### Application Security
- ✅ CSRF protection enabled
- ✅ Secure session cookies
- ✅ Password hashing with bcrypt
- ✅ SQL injection prevention
- ✅ File upload restrictions
- ✅ Rate limiting

## 📊 Monitoring & Maintenance

### Service Status
```bash
# Check all services
sudo systemctl status rv4-credit-dashboard nginx mysql redis-server

# View application logs
sudo journalctl -u rv4-credit-dashboard -f

# View Nginx logs
sudo tail -f /var/log/nginx/rv4-error.log
sudo tail -f /var/log/nginx/rv4-access.log
```

### Database Management
```bash
# Access MySQL console
mysql -u rv4user -p rv4_credit_db

# Create manual backup
mysqldump -u rv4user -p rv4_credit_db | gzip > backup_$(date +%Y%m%d).sql.gz

# Monitor database size
mysql -u rv4user -p -e "SELECT table_schema AS 'Database', ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)' FROM information_schema.tables WHERE table_schema='rv4_credit_db';"
```

### Performance Monitoring
```bash
# System resource usage
htop
df -h
free -h

# Application performance
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:8000/

# Database performance
mysql -u rv4user -p -e "SHOW PROCESSLIST;"
```

## 🔄 Backup Strategy

### Automated Backups (Included in deployment)
- **Database backup**: Daily at 2:00 AM (7-day retention)
- **Application data backup**: Daily at 3:00 AM (7-day retention)
- **Log rotation**: Daily with 30-day retention

### Manual Backup Commands
```bash
# Run backup scripts manually
cd /home/rv4user/apps/rv4-credit-dashboard
./backup_db.sh
./backup_app.sh

# Verify backups
ls -la /home/rv4user/backups/

# Test restore procedure
gunzip -c /home/rv4user/backups/db_backup_YYYYMMDD_HHMMSS.sql.gz | mysql -u rv4user -p rv4_credit_db
```

## 🌐 SSL Certificate Setup

### With Domain Name
```bash
# Install Let's Encrypt certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test automatic renewal
sudo certbot renew --dry-run

# Setup auto-renewal cron job
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### Self-Signed Certificate (Development)
```bash
# Generate self-signed certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/rv4-selfsigned.key \
    -out /etc/ssl/certs/rv4-selfsigned.crt

# Update Nginx configuration for HTTPS
sudo nano /etc/nginx/sites-available/rv4-credit-dashboard
```

## 🚨 Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check service status
sudo systemctl status rv4-credit-dashboard

# View detailed logs
sudo journalctl -u rv4-credit-dashboard --no-pager

# Check Python environment
cd /home/rv4user/apps/rv4-credit-dashboard
source venv/bin/activate
python3 -c "import app_updated; print('App imports successfully')"
```

#### Database Connection Issues
```bash
# Test database connection
mysql -u rv4user -p rv4_credit_db -e "SELECT 1;"

# Check MySQL service
sudo systemctl status mysql

# Review MySQL logs
sudo tail -f /var/log/mysql/error.log
```

#### High Memory Usage
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head -10

# Restart services if needed
sudo systemctl restart rv4-credit-dashboard
```

#### Nginx Configuration Issues
```bash
# Test Nginx configuration
sudo nginx -t

# Reload Nginx configuration
sudo systemctl reload nginx

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

## 📞 Support & Updates

### Getting Updates
```bash
# Update application code
cd /home/rv4user/apps/rv4-credit-dashboard
git pull origin main

# Update Python dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart application
sudo systemctl restart rv4-credit-dashboard
```

### System Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update security patches only
sudo unattended-upgrade

# Reboot if kernel updates were installed
sudo reboot
```

---

**Last Updated**: September 11, 2025  
**Deployment Version**: 1.0.0  
**Tested On**: Ubuntu 22.04 LTS, Digital Ocean Droplets
