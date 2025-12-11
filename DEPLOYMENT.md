# Production Deployment Guide

## Deployment Options

### Option 1: Using Gunicorn + Nginx (Recommended)

#### Prerequisites
- Linux server (Ubuntu 20.04+)
- Python 3.8+
- Nginx installed
- Supervisor or systemd

#### Step 1: Server Setup
```bash
# SSH into your server
ssh user@your_server_ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv nginx supervisor
```

#### Step 2: Deploy Application
```bash
# Create app directory
sudo mkdir -p /var/www/swing_trading_app
cd /var/www/swing_trading_app

# Clone or copy your application
# git clone <your_repo> .
# or
scp -r swing_trading_app/* user@server:/var/www/swing_trading_app/

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Deactivate venv
deactivate
```

#### Step 3: Configure Gunicorn

Create `/var/www/swing_trading_app/wsgi.py`:
```python
from app import app

if __name__ == "__main__":
    app.run()
```

#### Step 4: Create Systemd Service

Create `/etc/systemd/system/swing_trading.service`:
```ini
[Unit]
Description=BSE Swing Trading Application
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/swing_trading_app
Environment="PATH=/var/www/swing_trading_app/venv/bin"
ExecStart=/var/www/swing_trading_app/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind unix:/var/www/swing_trading_app/swing_trading.sock \
    --timeout 120 \
    wsgi:app
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

#### Step 5: Configure Nginx

Create `/etc/nginx/sites-available/swing_trading`:
```nginx
upstream swing_trading_app {
    server unix:/var/www/swing_trading_app/swing_trading.sock fail_timeout=0;
}

server {
    listen 80;
    server_name your_domain.com www.your_domain.com;

    client_max_body_size 10M;

    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://swing_trading_app;
    }

    location /static/ {
        alias /var/www/swing_trading_app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

#### Step 6: Enable and Start Service
```bash
# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/swing_trading /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Enable and start Swing Trading service
sudo systemctl enable swing_trading
sudo systemctl start swing_trading
sudo systemctl status swing_trading
```

#### Step 7: SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your_domain.com -d www.your_domain.com

# Auto-renewal is configured by default
sudo systemctl enable certbot.timer
```

---

### Option 2: Using Docker

#### Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/health')" || exit 1

# Run application
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "app:app"]
```

#### Create docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=False
    restart: unless-stopped
    volumes:
      - ./watchlist.json:/app/watchlist.json
```

#### Deploy with Docker
```bash
# Build image
docker build -t swing_trading_app .

# Run container
docker run -d \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  --restart unless-stopped \
  --name swing_trading \
  swing_trading_app

# Or use docker-compose
docker-compose up -d
```

---

### Option 3: Heroku Deployment

#### Create Procfile
```
web: gunicorn -w 4 -b 0.0.0.0:$PORT app:app
```

#### Deploy
```bash
# Install Heroku CLI
curl https://cli.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create your-app-name

# Deploy
git push heroku main

# Check logs
heroku logs --tail
```

---

## Production Configuration

### Environment Variables (.env)
```
FLASK_ENV=production
FLASK_DEBUG=False
CACHE_DURATION_MINUTES=15
MAX_WORKERS=4
SECRET_KEY=your_secure_random_key_here
```

### Logging Configuration

Add to `app.py`:
```python
import logging
from logging.handlers import RotatingFileHandler
import os

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler('logs/swing_trading.log', 
                                       maxBytes=10240000, 
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('Swing trading app startup')
```

---

## Performance Optimization

### Caching Strategy
```python
# In app.py - Implement Redis caching
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/top-stocks')
@cache.cached(timeout=900)  # Cache for 15 minutes
def get_top_stocks():
    # ... existing code
```

### Database for Analytics (Optional)
```python
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/swing_trading'
db = SQLAlchemy(app)

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10))
    entry_price = db.Column(db.Float)
    target_price = db.Column(db.Float)
    stop_loss = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## Monitoring & Maintenance

### Uptime Monitoring
```bash
# Using systemd
sudo systemctl status swing_trading

# Check logs
sudo journalctl -u swing_trading -f

# Check Nginx
sudo systemctl status nginx
```

### Automated Backups
```bash
# Create backup script: backup.sh
#!/bin/bash
BACKUP_DIR="/backups/swing_trading"
mkdir -p $BACKUP_DIR
cp /var/www/swing_trading_app/watchlist.json $BACKUP_DIR/watchlist_$(date +%Y%m%d_%H%M%S).json

# Add to crontab for daily backups
0 2 * * * /path/to/backup.sh
```

### Log Rotation
```bash
# Create /etc/logrotate.d/swing_trading
/var/www/swing_trading_app/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload swing_trading > /dev/null 2>&1 || true
    endscript
}
```

---

## Security Considerations

### 1. HTTPS/SSL (Required)
```bash
# Already configured with Certbot above
# Force HTTPS redirect in Nginx
if ($scheme != "https") {
    return 301 https://$server_name$request_uri;
}
```

### 2. Rate Limiting
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/top-stocks')
@limiter.limit("20 per hour")
def get_top_stocks():
    # ... existing code
```

### 3. CORS Configuration
```python
from flask_cors import CORS

# Restrict to specific domains
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com"],
        "methods": ["GET", "POST", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})
```

### 4. API Key Authentication (Optional)
```python
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.environ.get('API_KEY'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/top-stocks')
@require_api_key
def get_top_stocks():
    # ... existing code
```

---

## Scaling Considerations

### Horizontal Scaling
- Use load balancer (AWS ELB, Nginx)
- Run multiple gunicorn workers (4-8)
- Use Redis for caching across instances
- Store watchlist in database instead of JSON file

### Vertical Scaling
- Increase gunicorn workers
- Increase server resources (RAM, CPU)
- Optimize database queries
- Cache frequently requested data

---

## Health Checks

### Status Page
```python
@app.route('/api/health')
def health_check():
    try:
        # Test data fetching
        fetcher = BSEDataFetcher()
        fetcher.get_current_price("RELIANCE.BO")
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'data_source': 'yfinance',
            'uptime': get_uptime()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503
```

---

## Performance Metrics

### Expected Performance
- Page load: < 2 seconds
- API response: < 1 second (cached)
- First data fetch: < 30 seconds
- Concurrent users: 100+ (with proper resources)

### Monitoring Tools
- New Relic
- DataDog
- Sentry (error tracking)
- CloudWatch (AWS)

---

## Disaster Recovery

### Backup Strategy
1. Daily automated backups of watchlist.json
2. Database backups (if using database)
3. Configuration files backed up
4. Keep 30 days of backups

### Restore Process
```bash
# Restore from backup
cp /backups/watchlist_20231210.json /var/www/swing_trading_app/watchlist.json

# Restart service
sudo systemctl restart swing_trading
```

---

## Troubleshooting Deployment

### 502 Bad Gateway
```
Check: gunicorn is running
sudo systemctl status swing_trading
sudo journalctl -u swing_trading -f
```

### High CPU Usage
```
Reduce worker count or add resources
Monitor data fetching performance
Check for infinite loops in analysis
```

### Memory Issues
```
Reduce cache duration
Implement garbage collection
Monitor yfinance calls
```

---

**For production deployment support, consult your DevOps team or hosting provider.**
