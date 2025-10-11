#!/bin/bash

# RV4 Credit Dashboard - Server Setup Script for Ubuntu 22.04
# Run this script as root on a fresh Ubuntu 22.04 droplet

set -e

echo "🚀 Starting RV4 Credit Dashboard server setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root"
    exit 1
fi

# Update system
print_status "Updating system packages..."
apt update && apt upgrade -y

# Install essential packages
print_status "Installing essential packages..."
apt install -y \
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
    python3-certbot-nginx \
    ufw \
    logrotate

# Install Node.js
print_status "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# Create application user
print_status "Creating application user..."
if ! id "rv4user" &>/dev/null; then
    adduser --disabled-password --gecos "" rv4user
    usermod -aG sudo rv4user
    print_status "User 'rv4user' created successfully"
else
    print_warning "User 'rv4user' already exists"
fi

# Setup SSH access for rv4user
print_status "Setting up SSH access for rv4user..."
mkdir -p /home/rv4user/.ssh
if [ -f /root/.ssh/authorized_keys ]; then
    cp /root/.ssh/authorized_keys /home/rv4user/.ssh/
    chown -R rv4user:rv4user /home/rv4user/.ssh
    chmod 700 /home/rv4user/.ssh
    chmod 600 /home/rv4user/.ssh/authorized_keys
    print_status "SSH keys copied for rv4user"
fi

# Configure UFW firewall
print_status "Configuring UFW firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

# Secure MySQL installation
print_status "Securing MySQL installation..."
mysql -e "DELETE FROM mysql.user WHERE User='';"
mysql -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
mysql -e "DROP DATABASE IF EXISTS test;"
mysql -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';"
mysql -e "FLUSH PRIVILEGES;"

# Configure fail2ban
print_status "Configuring fail2ban..."
cat > /etc/fail2ban/jail.local << EOF
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

# Start and enable services
print_status "Starting and enabling services..."
systemctl enable nginx
systemctl enable mysql
systemctl enable redis-server
systemctl enable fail2ban

systemctl start nginx
systemctl start mysql
systemctl start redis-server
systemctl start fail2ban

# Create application directories
print_status "Creating application directories..."
su - rv4user -c "mkdir -p /home/rv4user/apps"
su - rv4user -c "mkdir -p /home/rv4user/backups"
su - rv4user -c "mkdir -p /home/rv4user/logs"

# Set timezone
print_status "Setting timezone..."
timedatectl set-timezone UTC

# Create swap file (if not exists and less than 2GB RAM)
TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.0f", $2}')
if [ "$TOTAL_MEM" -lt 2048 ] && [ ! -f /swapfile ]; then
    print_status "Creating swap file..."
    fallocate -l 1G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

# Configure system limits
print_status "Configuring system limits..."
cat >> /etc/security/limits.conf << EOF
rv4user soft nofile 65536
rv4user hard nofile 65536
rv4user soft nproc 4096
rv4user hard nproc 4096
EOF

# Configure sysctl for better performance
print_status "Optimizing kernel parameters..."
cat >> /etc/sysctl.conf << EOF
# Network performance optimization
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_congestion_control = bbr

# File system optimization
fs.file-max = 65536
EOF

sysctl -p

print_status "✅ Server setup completed successfully!"
print_status "Next steps:"
print_status "1. Login as rv4user: ssh rv4user@YOUR_SERVER_IP"
print_status "2. Run the application deployment script"
print_status "3. Configure your domain and SSL certificate"

print_warning "Remember to:"
print_warning "- Change default passwords"
print_warning "- Configure your domain name"
print_warning "- Setup monitoring and alerts"
print_warning "- Test backup procedures"
