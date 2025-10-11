# RV4 Credit Dashboard - Docker Deployment

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- 2GB+ RAM available
- Domain name (optional)

### 1. Create docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: rv4-credit-dashboard
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql+pymysql://rv4user:secure_password@db:3306/rv4_credit_db
      - SECRET_KEY=your-super-secret-key-change-this
      - FLASK_ENV=production
      - DEBUG=False
    volumes:
      - ./data:/app/data
      - ./weights:/app/weights
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    depends_on:
      - db
      - redis
    networks:
      - rv4-network

  db:
    image: mysql:8.0
    container_name: rv4-mysql
    restart: unless-stopped
    environment:
      - MYSQL_ROOT_PASSWORD=root_password_change_this
      - MYSQL_DATABASE=rv4_credit_db
      - MYSQL_USER=rv4user
      - MYSQL_PASSWORD=secure_password
    volumes:
      - mysql_data:/var/lib/mysql
      - ./deployment/mysql-init:/docker-entrypoint-initdb.d
    ports:
      - "3306:3306"
    networks:
      - rv4-network

  redis:
    image: redis:7-alpine
    container_name: rv4-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    networks:
      - rv4-network

  nginx:
    image: nginx:alpine
    container_name: rv4-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deployment/nginx.conf:/etc/nginx/nginx.conf
      - ./static:/var/www/static
      - ./uploads:/var/www/uploads
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    networks:
      - rv4-network

volumes:
  mysql_data:

networks:
  rv4-network:
    driver: bridge
```

### 2. Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data weights uploads application_data report

# Set permissions
RUN chmod -R 755 logs data weights uploads application_data report

# Create non-root user
RUN useradd -m -u 1000 rv4user && chown -R rv4user:rv4user /app
USER rv4user

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "30", "app_updated:app"]
```

### 3. Deploy with Docker Compose
```bash
# Clone repository
git clone <your-repo-url>
cd rv4-credit-dashboard

# Build and start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app
```

### 4. Initialize Database
```bash
# Create admin user
docker-compose exec app python3 -c "
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
    print('Admin user created')
"
```

## Production Docker Deployment

### 1. Environment Configuration
Create `.env` file:
```bash
# Database
MYSQL_ROOT_PASSWORD=super_secure_root_password
MYSQL_PASSWORD=secure_user_password
DATABASE_URL=mysql+pymysql://rv4user:secure_user_password@db:3306/rv4_credit_db

# Application
SECRET_KEY=your-super-secret-key-minimum-32-characters
FLASK_ENV=production
DEBUG=False

# Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
WTF_CSRF_ENABLED=True
```

### 2. Production docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: rv4-credit-dashboard
    restart: unless-stopped
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - FLASK_ENV=${FLASK_ENV}
      - DEBUG=${DEBUG}
    volumes:
      - ./data:/app/data
      - ./weights:/app/weights
      - ./uploads:/app/uploads
      - ./logs:/app/logs
      - ./backups:/app/backups
    depends_on:
      - db
      - redis
    networks:
      - rv4-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: mysql:8.0
    container_name: rv4-mysql
    restart: unless-stopped
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - MYSQL_DATABASE=rv4_credit_db
      - MYSQL_USER=rv4user
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./backups:/backups
    networks:
      - rv4-network
    command: --default-authentication-plugin=mysql_native_password

  redis:
    image: redis:7-alpine
    container_name: rv4-redis
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - rv4-network

  nginx:
    image: nginx:alpine
    container_name: rv4-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deployment/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./deployment/nginx/sites:/etc/nginx/sites-available
      - ./static:/var/www/static:ro
      - ./uploads:/var/www/uploads:ro
      - ./ssl:/etc/nginx/ssl:ro
      - nginx_logs:/var/log/nginx
    depends_on:
      - app
    networks:
      - rv4-network

  backup:
    image: mysql:8.0
    container_name: rv4-backup
    restart: "no"
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
    volumes:
      - ./backups:/backups
      - ./deployment/backup.sh:/backup.sh
    depends_on:
      - db
    networks:
      - rv4-network
    command: /bin/bash -c "chmod +x /backup.sh && /backup.sh"

volumes:
  mysql_data:
  redis_data:
  nginx_logs:

networks:
  rv4-network:
    driver: bridge
```

### 3. Nginx Configuration for Docker
Create `deployment/nginx/nginx.conf`:
```nginx
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    # Upstream
    upstream app {
        server app:8000;
    }

    server {
        listen 80;
        server_name _;

        # Security
        server_tokens off;

        # File upload size
        client_max_body_size 16M;

        # Rate limiting
        limit_req zone=api burst=20 nodelay;

        # Static files
        location /static/ {
            alias /var/www/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
            access_log off;
        }

        location /uploads/ {
            alias /var/www/uploads/;
            expires 1d;
            add_header Cache-Control "public";
        }

        # API endpoints (stricter rate limiting)
        location /api/ {
            limit_req zone=api burst=10 nodelay;
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Login endpoint (very strict rate limiting)
        location /auth/login {
            limit_req zone=login burst=3 nodelay;
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Main application
        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_redirect off;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Health check
        location /health {
            proxy_pass http://app;
            access_log off;
        }
    }
}
```

### 4. Backup Script for Docker
Create `deployment/backup.sh`:
```bash
#!/bin/bash

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
mysqldump -h db -u root -p$MYSQL_ROOT_PASSWORD rv4_credit_db > $BACKUP_DIR/rv4_db_backup_$DATE.sql
gzip $BACKUP_DIR/rv4_db_backup_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "rv4_db_backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: rv4_db_backup_$DATE.sql.gz"
```

### 5. SSL with Let's Encrypt in Docker
Create `deployment/ssl-setup.sh`:
```bash
#!/bin/bash

DOMAIN="your-domain.com"
EMAIL="your-email@example.com"

# Install certbot
docker run -it --rm --name certbot \
    -v "${PWD}/ssl:/etc/letsencrypt" \
    -v "${PWD}/ssl-challenge:/var/www/certbot" \
    certbot/certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

# Setup auto-renewal
echo "0 12 * * * docker run --rm --name certbot -v \"${PWD}/ssl:/etc/letsencrypt\" -v \"${PWD}/ssl-challenge:/var/www/certbot\" certbot/certbot renew --quiet" | crontab -
```

## Monitoring and Maintenance

### 1. Health Monitoring
```bash
# Check service health
docker-compose ps

# View logs
docker-compose logs -f app
docker-compose logs -f nginx
docker-compose logs -f db

# Monitor resource usage
docker stats
```

### 2. Database Maintenance
```bash
# Backup database
docker-compose exec db mysqldump -u root -p rv4_credit_db > backup.sql

# Restore database
docker-compose exec -T db mysql -u root -p rv4_credit_db < backup.sql

# Access MySQL console
docker-compose exec db mysql -u root -p
```

### 3. Application Updates
```bash
# Update application
git pull origin main
docker-compose build app
docker-compose up -d app

# Update all services
docker-compose pull
docker-compose up -d
```

### 4. Scaling
```bash
# Scale application containers
docker-compose up -d --scale app=3

# Load balance with nginx upstream
# Add to nginx.conf upstream block:
# server app:8000;
# server app:8000;
# server app:8000;
```

## Troubleshooting

### Common Issues
1. **Database connection errors**: Check DATABASE_URL and network connectivity
2. **Permission issues**: Ensure volumes have correct ownership
3. **Memory issues**: Increase Docker memory limits
4. **SSL certificate issues**: Check domain DNS and firewall settings

### Debugging Commands
```bash
# Container logs
docker-compose logs -f [service_name]

# Execute commands in container
docker-compose exec app bash
docker-compose exec db mysql -u root -p

# Check network connectivity
docker-compose exec app ping db
docker-compose exec app curl -I http://localhost:8000/health

# Monitor resources
docker stats
docker system df
```

---

This Docker deployment provides a complete, production-ready setup with proper security, monitoring, and backup capabilities.
