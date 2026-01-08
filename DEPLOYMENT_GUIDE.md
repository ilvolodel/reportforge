# ReportForge Deployment Guide 🚀

Complete guide for deploying ReportForge on the DigitalOcean droplet.

## 📋 Prerequisites

- Droplet: `161.35.214.46` (SSH: `root@10.135.215.172`)
- Domain: `reportforge.brainaihub.tech` → pointing to droplet IP
- Docker & Docker Compose installed on droplet
- Main nginx proxy already running on droplet (for SSL/routing)

## 🔧 Step 1: Initial Setup on Droplet

```bash
# SSH to droplet
ssh root@10.135.215.172
# Password: Fr3qu3nc1.

# Clone repository
cd /opt
git clone https://github.com/ilvolodel/reportforge.git
cd reportforge

# Verify files
ls -la
```

## 🔐 Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with production values
nano .env
```

**Important variables to update:**

```bash
# Database - CHANGE PASSWORD!
POSTGRES_PASSWORD=your_secure_random_password_here

# Authentication - GENERATE RANDOM SECRET!
SECRET_KEY=use_openssl_rand_hex_32_to_generate_this

# Email (SMTP) - REQUIRED FOR MAGIC LINKS!
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@infocert.it
SMTP_PASSWORD=your_smtp_app_password
SMTP_FROM=ReportForge <noreply@infocert.it>

# Application
APP_URL=https://reportforge.brainaihub.tech
DEBUG=false
ENVIRONMENT=production
```

**Generate secure secrets:**

```bash
# Generate SECRET_KEY (use this output in .env)
openssl rand -hex 32

# Generate POSTGRES_PASSWORD (use this output in .env)
openssl rand -base64 24
```

## 🐳 Step 3: Deploy Application

```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
sudo ./deploy.sh
```

This will:
1. Build Docker images
2. Start PostgreSQL, Backend, and Nginx containers
3. Run database migrations
4. Start all services

## 🌐 Step 4: Configure Main Nginx Proxy

The droplet has a main nginx that handles SSL and routes traffic. We need to add ReportForge configuration.

```bash
# Create nginx config for ReportForge
nano /etc/nginx/sites-available/reportforge.brainaihub.tech
```

**Add this configuration:**

```nginx
upstream reportforge_backend {
    server 127.0.0.1:8080;
}

server {
    listen 80;
    server_name reportforge.brainaihub.tech;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name reportforge.brainaihub.tech;

    # SSL certificates (update paths if needed)
    ssl_certificate /etc/letsencrypt/live/reportforge.brainaihub.tech/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/reportforge.brainaihub.tech/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/reportforge.brainaihub.tech/chain.pem;

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/reportforge-access.log;
    error_log /var/log/nginx/reportforge-error.log;

    # Max upload size
    client_max_body_size 50M;

    # Proxy to ReportForge Docker container
    location / {
        proxy_pass http://reportforge_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_redirect off;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

**Enable site and reload nginx:**

```bash
# Enable site
ln -s /etc/nginx/sites-available/reportforge.brainaihub.tech /etc/nginx/sites-enabled/

# Test nginx configuration
nginx -t

# Reload nginx
systemctl reload nginx
```

## 🔒 Step 5: Setup SSL Certificate (if not exists)

```bash
# Install certbot (if not already installed)
apt-get update
apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate
certbot --nginx -d reportforge.brainaihub.tech

# Certbot will automatically configure nginx
# Follow prompts to set up auto-renewal
```

## ✅ Step 6: Verify Deployment

```bash
# Check container status
cd /opt/reportforge
docker-compose ps

# All services should show "Up" and "healthy"
```

**Expected output:**
```
NAME                    STATUS              PORTS
reportforge-backend     Up (healthy)        
reportforge-db          Up (healthy)        
reportforge-nginx       Up (healthy)        0.0.0.0:8080->80/tcp
```

**Test endpoints:**

```bash
# Test health check (from droplet)
curl http://localhost:8080/health

# Test external access
curl https://reportforge.brainaihub.tech/health
```

## 📊 Step 7: Access Application

Open browser: **https://reportforge.brainaihub.tech**

You should see the login page.

## 🔧 Maintenance Commands

### View Logs

```bash
cd /opt/reportforge

# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f nginx
```

### Restart Services

```bash
cd /opt/reportforge

# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Update Application

```bash
cd /opt/reportforge

# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check status
docker-compose ps
```

### Database Access

```bash
cd /opt/reportforge

# PostgreSQL shell
docker-compose exec postgres psql -U reportforge

# Backup database
docker-compose exec postgres pg_dump -U reportforge reportforge > backup_$(date +%Y%m%d).sql

# Restore database
cat backup_20260107.sql | docker-compose exec -T postgres psql -U reportforge reportforge
```

### Run Migrations

```bash
cd /opt/reportforge

# Run pending migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"
```

### Backend Shell

```bash
cd /opt/reportforge
docker-compose exec backend bash
```

## 🚨 Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs backend

# Check if port 8080 is in use
netstat -tulpn | grep 8080

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Database connection errors

```bash
# Check postgres is running
docker-compose ps postgres

# Check postgres logs
docker-compose logs postgres

# Verify DATABASE_URL in .env matches docker-compose.yml
```

### Can't access from browser

```bash
# Check main nginx
systemctl status nginx
nginx -t

# Check if docker nginx is running
docker-compose ps nginx

# Check port binding
netstat -tulpn | grep 8080

# Check DNS
nslookup reportforge.brainaihub.tech
```

### SSL certificate issues

```bash
# Check certificate
openssl s_client -connect reportforge.brainaihub.tech:443 -servername reportforge.brainaihub.tech

# Renew certificate
certbot renew --nginx

# Check auto-renewal timer
systemctl status certbot.timer
```

## 🔄 Rollback Procedure

```bash
cd /opt/reportforge

# Stop containers
docker-compose down

# Checkout previous version
git log  # Find commit hash
git checkout <commit-hash>

# Restart
docker-compose up -d
```

## 📧 SMTP Configuration Notes

For Gmail SMTP:
1. Enable 2FA on Gmail account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use App Password in `SMTP_PASSWORD` (not your Gmail password)

For other SMTP providers:
- Check their documentation for host/port
- Common ports: 587 (TLS), 465 (SSL), 25 (unencrypted - not recommended)

## 🎯 Next Steps

Once deployed:
1. Access https://reportforge.brainaihub.tech
2. Enter your email for magic link
3. Check email and click link to login
4. Start adding projects and data

## 📞 Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Check container status: `docker-compose ps`
3. Check main nginx: `systemctl status nginx`
4. Check SSL: `certbot certificates`

---

**Deployment completed! 🎉**
