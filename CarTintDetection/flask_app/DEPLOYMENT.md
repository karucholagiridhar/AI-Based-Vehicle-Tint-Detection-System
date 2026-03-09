# 🚀 Production Deployment Guide

## Overview
This guide walks you through deploying your AI-Based Vehicle Tint Detection System to production using modern best practices.

## Prerequisites
- Git repository
- Python 3.8+
- Production database (PostgreSQL recommended)
- Cloud hosting account (Heroku, AWS, DigitalOcean, etc.)
- Domain name (optional)

## 📋 Pre-Deployment Checklist

### 1. Code Quality
- [ ] All tests passing
- [ ] No console.log statements in production code
- [ ] No hardcoded credentials
- [ ] Error handling implemented
- [ ] Input validation on all forms
- [ ] CSRF protection enabled

### 2. Security
- [ ] SECRET_KEY is strong and random
- [ ] Environment variables configured
- [ ] HTTPS enforced
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] File upload validation
- [ ] SQL injection protection (using ORM)
- [ ] XSS protection enabled

### 3. Performance
- [ ] Static files compressed (gzip)
- [ ] Images optimized
- [ ] Database queries optimized
- [ ] Caching configured
- [ ] CDN setup (optional)

### 4. Monitoring
- [ ] Error tracking (Sentry)
- [ ] Logging configured
- [ ] Uptime monitoring
- [ ] Performance monitoring
- [ ] Database backup strategy

## 🔧 Environment Configuration

### Create `.env.production` file
```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=<generate-strong-random-key>
DEBUG=False

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Roboflow API
ROBOFLOW_API_URL=https://serverless.roboflow.com
ROBOFLOW_API_KEY=your_api_key_here
MODEL_ID=your_model_id

# Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# Uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
UPLOAD_FOLDER=/var/www/uploads

# Redis (optional, for caching)
REDIS_URL=redis://localhost:6379/0

# Sentry (optional, for error tracking)
SENTRY_DSN=your_sentry_dsn_here
```

### Generate SECRET_KEY
```python
import secrets
print(secrets.token_urlsafe(32))
```

## 🐳 Docker Deployment

### 1. Create `Dockerfile`
```dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create upload directory
RUN mkdir -p /app/uploads && chmod 777 /app/uploads

# Expose port
EXPOSE 5000

# Run with gunicorn
CMD ["gunicorn", "--config", "gunicorn.conf.py", "run:app"]
```

### 2. Create `docker-compose.yml`
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://postgres:password@db:5432/tintdetect
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads
    restart: always

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=tintdetect
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./uploads:/var/www/uploads
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: always

volumes:
  postgres_data:
```

### 3. Create `gunicorn.conf.py`
```python
import multiprocessing

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "tint_detection"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if not using nginx)
# keyfile = "/path/to/key.pem"
# certfile = "/path/to/cert.pem"
```

### 4. Create `nginx.conf`
```nginx
events {
    worker_connections 1024;
}

http {
    upstream app {
        server web:5000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        
        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' https:; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com;" always;

        # File upload size limit
        client_max_body_size 16M;

        # Gzip compression
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_types text/plain text/css text/xml text/javascript application/json application/javascript;

        # Static files
        location /static/ {
            alias /var/www/uploads/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        # Proxy to Flask app
        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_redirect off;
        }
    }
}
```

## ☁️ Cloud Platform Deployment

### Heroku

1. **Install Heroku CLI**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

2. **Create `Procfile`**
```
web: gunicorn --config gunicorn.conf.py run:app
```

3. **Create `runtime.txt`**
```
python-3.10.12
```

4. **Deploy**
```bash
# Login
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
heroku config:set ROBOFLOW_API_KEY=your_key_here
heroku config:set ROBOFLOW_API_URL=https://serverless.roboflow.com
heroku config:set MODEL_ID=your_model_id

# Push to Heroku
git push heroku main

# Run migrations (if using Flask-Migrate)
heroku run flask db upgrade

# Open app
heroku open
```

### AWS EC2

1. **Launch EC2 instance** (Ubuntu 22.04)

2. **SSH into instance**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

3. **Install dependencies**
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx postgresql -y
```

4. **Clone repository**
```bash
git clone your-repo-url
cd your-repo
```

5. **Setup Python environment**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

6. **Configure systemd service**
Create `/etc/systemd/system/tintdetect.service`:
```ini
[Unit]
Description=Tint Detection App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/your-repo
Environment="PATH=/home/ubuntu/your-repo/venv/bin"
EnvironmentFile=/home/ubuntu/your-repo/.env.production
ExecStart=/home/ubuntu/your-repo/venv/bin/gunicorn --config gunicorn.conf.py run:app

[Install]
WantedBy=multi-user.target
```

7. **Start service**
```bash
sudo systemctl start tintdetect
sudo systemctl enable tintdetect
sudo systemctl status tintdetect
```

8. **Configure Nginx** (use `nginx.conf` from above)

## 🔍 Monitoring & Logging

### Setup Sentry for Error Tracking

1. **Install Sentry SDK**
```bash
pip install sentry-sdk[flask]
```

2. **Add to `app/__init__.py`**
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
    environment="production"
)
```

### Setup Logging

Add to `app/__init__.py`:
```python
import logging
from logging.handlers import RotatingFileHandler
import os

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler(
        'logs/tintdetect.log',
        maxBytes=10240000,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Tint Detection startup')
```

## 🔄 CI/CD Pipeline (GitHub Actions)

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Heroku
        uses: akhileshns/heroku-deploy@v3.12.12
        with:
          heroku_api_key: ${{secrets.HEROKU_API_KEY}}
          heroku_app_name: "your-app-name"
          heroku_email: "your-email@example.com"
```

## 📊 Database Migrations

Using Flask-Migrate:

```bash
# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade

# Production deployment
heroku run flask db upgrade  # Heroku
# or
ssh ubuntu@your-ec2 "cd your-repo && source venv/bin/activate && flask db upgrade"  # EC2
```

## 🔐 SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal (already configured)
sudo certbot renew --dry-run
```

## 📈 Performance Optimization

### Enable Response Caching
```python
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.getenv('REDIS_URL')
})

@main_bp.route('/stats')
@cache.cached(timeout=300)  # Cache for 5 minutes
def stats():
    # ...
```

### Database Connection Pooling
```python
# config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}
```

## 🔧 Maintenance

### Backup Database
```bash
# PostgreSQL
pg_dump dbname > backup.sql

# Restore
psql dbname < backup.sql
```

### Monitor Disk Space
```bash
df -h
du -sh /var/www/uploads
```

### View Logs
```bash
# Application logs
tail -f logs/tintdetect.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# System logs
journalctl -u tintdetect -f
```

## 🆘 Troubleshooting

### App won't start
```bash
# Check logs
heroku logs --tail  # Heroku
journalctl -u tintdetect -n 100  # EC2

# Check environment variables
heroku config  # Heroku
cat .env.production  # EC2
```

### Database connection errors
```bash
# Test connection
psql $DATABASE_URL

# Reset database
flask db downgrade
flask db upgrade
```

### High memory usage
```bash
# Check processes
htop

# Reduce gunicorn workers
# Edit gunicorn.conf.py: workers = 2
```

## 📚 Additional Resources

- [Flask Deployment Documentation](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Heroku Python Guide](https://devcenter.heroku.com/articles/getting-started-with-python)

---

**Remember**: Always test deployments in a staging environment before deploying to production!
