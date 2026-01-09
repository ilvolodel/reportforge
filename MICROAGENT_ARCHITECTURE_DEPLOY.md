# MICROAGENT: ReportForge Architecture & Deployment

## 🎯 Purpose
This microagent documents the **proven architecture patterns** and **deployment procedures** for ReportForge, based on the successful TrustyVault reference implementation running on the same droplet.

**Last Updated**: 2026-01-08  
**Status**: ✅ DEPLOYED & FULLY OPERATIONAL WITH HTTPS + LOGIN PAGE COMPLETE  
**Current Commit**: 37e673c  
**Public URL**: https://reportforge.brainaihub.tech

---

## 🚨 CRITICAL RULES - READ FIRST!

### ❌ NEVER DO THIS:
1. **NEVER modify `/opt/proxy-nginx/nginx/nginx.conf` or files in `/opt/proxy-nginx/nginx/conf.d/`**
   - proxy-nginx is a SHARED service routing ALL applications on the droplet
   - Modifying it can break TrustyVault, PEC, MS365, Documents, TrustySign, and ALL other services
   - The proxy uses SNI (Server Name Indication) routing - it's NOT a traditional nginx reverse proxy

2. **NEVER restart proxy-nginx without explicit user approval**
   - Restarting affects ALL services on the entire droplet
   - If proxy-nginx breaks, the ENTIRE infrastructure goes down

3. **NEVER create config files in `/opt/proxy-nginx/nginx/conf.d/`**
   - SNI routing works differently - it reads hostnames from the main `nginx.conf` stream block
   - Adding traditional `server {}` blocks will cause conflicts and crashes

### ✅ ALWAYS DO THIS:
1. **ALWAYS use FULL container names in ALL configurations**
   - Database: `reportforge-db` (NOT `postgres` or `db`)
   - Backend: `reportforge-backend` (NOT `backend` or `app`)
   - Nginx: `reportforge-nginx` (NOT `nginx` or `web`)

2. **ALWAYS check logs before making changes**
   ```bash
   # Check nginx logs
   docker logs reportforge-nginx --tail 50
   cat /opt/reportforge/logs/nginx/error.log | tail -20
   
   # Check backend logs
   docker logs reportforge-backend --tail 50
   
   # Check proxy logs (only if needed)
   docker logs proxy-nginx --tail 50
   ```

3. **ALWAYS verify container names match in ALL files**
   - `docker-compose.yml` defines: `container_name: reportforge-backend`
   - `.env` must use: `DATABASE_URL=postgresql://...@reportforge-db:5432/...`
   - `nginx/conf.d/*.conf` must use: `proxy_pass http://reportforge-backend:8030;`
   - `entrypoint.sh` must use: `pg_isready -h reportforge-db ...`

---

## 🔍 Common Issues & Solutions

### Issue: 502 Bad Gateway
**Symptoms**: `curl https://reportforge.brainaihub.tech/` returns 502

**Diagnosis**:
```bash
# Step 1: Check nginx error logs
cat /opt/reportforge/logs/nginx/error.log | tail -20

# Step 2: Look for "Connection refused" errors
# Example error: "connect() failed (111: Connection refused) while connecting to upstream, 
#                 upstream: "http://172.19.0.10:8030/""
```

**Root Causes**:
1. **Wrong container name in nginx config** (MOST COMMON!)
   - Error shows: `upstream: "http://172.19.0.10:8030/"` (IP instead of hostname)
   - Fix: Check `nginx/conf.d/*.conf` uses `reportforge-backend:8030` NOT `backend:8030`

2. **Backend container not running**
   ```bash
   docker ps --filter name=reportforge-backend
   # If not running: docker compose up -d backend
   ```

3. **Backend not listening on port 8030**
   ```bash
   docker exec reportforge-backend netstat -tlnp | grep 8030
   # Should show uvicorn listening
   ```

**Solution**:
```bash
# Fix nginx config
sed -i 's/http:\/\/backend:8030/http:\/\/reportforge-backend:8030/g' \
    nginx/conf.d/reportforge.brainaihub.tech.conf

# Verify
grep proxy_pass nginx/conf.d/*.conf
# Should show: proxy_pass http://reportforge-backend:8030;

# Deploy
git add nginx/conf.d/ && git commit -m "Fix nginx upstream name" && git push
ssh root@10.135.215.172 "cd /opt/reportforge && git pull && docker compose restart nginx"
```

### Issue: Database Connection Failed
**Symptoms**: Backend logs show `could not connect to server` or `Connection refused`

**Root Cause**: Wrong hostname in `DATABASE_URL`

**Solution**:
```bash
# Check .env file on server
ssh root@10.135.215.172 "grep DATABASE_URL /opt/reportforge/.env"

# Must be: postgresql://reportforge:PASSWORD@reportforge-db:5432/reportforge
# NOT:     postgresql://reportforge:PASSWORD@postgres:5432/reportforge
# NOT:     postgresql://reportforge:PASSWORD@db:5432/reportforge
# NOT:     postgresql://reportforge:PASSWORD@localhost:5432/reportforge

# If wrong, fix it:
ssh root@10.135.215.172
nano /opt/reportforge/.env
# Change database hostname to: reportforge-db
docker compose restart backend
```

### Issue: Proxy-nginx Down (Connection Reset)
**Symptoms**: ALL services on brainaihub.tech return connection errors

**Emergency Rollback**:
```bash
# 1. Check what was changed
ssh root@10.135.215.172
cd /opt/proxy-nginx/nginx/conf.d
ls -la
# Look for new/modified files

# 2. Remove any new files you created
rm /opt/proxy-nginx/nginx/conf.d/reportforge.conf  # If you created this

# 3. Restart proxy
docker restart proxy-nginx

# 4. Wait 10 seconds and verify
sleep 10
curl -I https://trustyvault.brainaihub.tech/  # Should return 200 or 404, NOT connection error
```

**Prevention**: 
- NEVER create files in `/opt/proxy-nginx/nginx/conf.d/`
- SNI routing is configured ONLY in `/opt/proxy-nginx/nginx/nginx.conf` stream block
- If you need to add reportforge to proxy, user must manually add it to the stream map

---

## 📐 Architecture Overview

### Infrastructure Stack
```
┌─────────────────────────────────────────────────────────────┐
│                  proxy-nginx (SNI Router)                   │
│              Shared across all applications                 │
│         Routes traffic based on server_name (SNI)           │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            │    proxy-nginx_proxy-network   │
            │      (Docker Network)          │
            └───────────────┬───────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼────┐        ┌────▼────┐        ┌────▼────┐
   │  nginx  │        │ backend │        │  postgr │
   │  :18030 │───────▶│  :8030  │───────▶│  :5432  │
   │  :18430 │        │ FastAPI │        │   SQL   │
   └─────────┘        └─────────┘        └─────────┘
reportforge-nginx  reportforge-backend  reportforge-db
```

### Key Design Principles (TrustyVault Pattern)

1. **Single Network Architecture**
   - ✅ All containers on `proxy-network` (external)
   - ❌ NO separate `internal` network
   - **Why**: Simpler networking, DNS resolution works reliably, easier debugging

2. **Full Container Names for DNS - THIS IS CRITICAL!**
   - ✅ **CORRECT**: `reportforge-db` (full container name from docker-compose.yml)
   - ❌ **WRONG**: `postgres`, `db`, `backend`, `nginx` (service names - DO NOT USE!)
   - **Why**: Docker DNS uses container_name, NOT service name
   - **Where to use**:
     - `.env`: `DATABASE_URL=postgresql://user:pass@reportforge-db:5432/db`
     - `nginx/*.conf`: `proxy_pass http://reportforge-backend:8030;`
     - `entrypoint.sh`: `pg_isready -h reportforge-db -p 5432`
   - **Real incident**: Using `backend:8030` instead of `reportforge-backend:8030` in nginx config caused 502 errors for entire day!

3. **Simple Database Configuration**
   ```python
   # backend/app/database.py
   import os
   DATABASE_URL = os.getenv("DATABASE_URL")
   engine = create_engine(DATABASE_URL, pool_pre_ping=True)
   ```
   - ✅ Direct `os.getenv()` access
   - ❌ NO pydantic-settings complexity
   - **Why**: Works with Alembic, FastAPI, init scripts without config conflicts

4. **Declarative Database Init (No Alembic for Initial Setup)**
   ```python
   # backend/app/init_db.py
   from .database import Base, engine
   Base.metadata.create_all(bind=engine)
   ```
   - ✅ Idempotent, simple, robust
   - ❌ Alembic NOT used for initial table creation
   - **Why**: Faster startup, no migration race conditions, easier to debug

5. **Robust Entrypoint Pattern**
   ```bash
   # entrypoint.sh
   until pg_isready -h reportforge-db -p 5432 -U reportforge; do
       sleep 1
   done
   python -m app.init_db
   exec uvicorn app.main:app --host 0.0.0.0 --port 8030
   ```
   - ✅ Wait for postgres → init DB → start server
   - ❌ NO direct CMD with race conditions
   - **Why**: Eliminates 99% of startup failures

---

## 🏗️ Project Structure

```
/opt/reportforge/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── database.py          # Simple DB config (os.getenv)
│   │   ├── init_db.py           # Base.metadata.create_all()
│   │   ├── config.py            # App settings
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── user.py          # User, MagicLink, UserSession
│   │   │   ├── project.py       # Project, TeamMember, Client, etc.
│   │   │   ├── subscription.py  # Subscription, RevenueOneTime
│   │   │   └── report.py        # ReportVersion
│   │   ├── api/                 # API routes (future)
│   │   ├── schemas/             # Pydantic schemas (future)
│   │   ├── services/            # Business logic (future)
│   │   └── templates/           # Jinja2 templates (PDF, email)
│   └── requirements.txt
├── frontend/
│   └── static/                  # HTML, CSS, JS (future)
├── nginx/
│   └── conf.d/
│       └── default.conf         # Nginx config
├── logs/                        # Application logs (volume mount)
├── .env                         # Production secrets (NOT in git)
├── .env.example                 # Template with DATABASE_URL=reportforge-db
├── docker-compose.yml           # Single network, 3 services
├── Dockerfile                   # Multi-stage Python 3.11
├── entrypoint.sh                # Startup script
├── deploy.sh                    # Deployment automation
└── MICROAGENT_*.md              # Documentation
```

---

## 🔧 Docker Configuration

### docker-compose.yml
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: reportforge-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: reportforge
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: reportforge
      TZ: Europe/Rome
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - proxy-network  # ✅ Single network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U reportforge -d reportforge"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: .
    container_name: reportforge-backend
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
      - ./.env:/app/.env:ro
    env_file:
      - ./.env
    environment:
      - TZ=Europe/Rome
      - PYTHONUNBUFFERED=1
      - PORT=8030
    depends_on:
      postgres:
        condition: service_healthy  # ✅ Wait for DB
    networks:
      - proxy-network  # ✅ Same network as postgres
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8030/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    container_name: reportforge-nginx
    restart: unless-stopped
    ports:
      - "18030:80"   # HTTP (for ACME challenges)
      - "18430:443"  # HTTPS (SSL termination)
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - swissknife_ssl-data:/etc/letsencrypt:ro  # Shared SSL
      - swissknife_certbot-webroot:/var/www/certbot
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - backend
    networks:
      - proxy-network  # ✅ Same network
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
    driver: local
  swissknife_ssl-data:
    external: true
    name: swissknife_ssl-data
  swissknife_certbot-webroot:
    external: true
    name: swissknife_certbot-webroot

networks:
  proxy-network:
    external: true
    name: proxy-nginx_proxy-network  # ✅ Shared with all apps
```

### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libpq-dev libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info curl \
    ca-certificates git postgresql-client \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy application code
COPY backend /app/backend
COPY frontend /app/frontend
COPY entrypoint.sh /app/entrypoint.sh

# Create directories and set permissions
RUN mkdir -p /app/logs && chmod +x /app/entrypoint.sh

# Capture git commit
ARG GIT_COMMIT=unknown
RUN echo "$GIT_COMMIT" > /app/.git_commit

ENV PYTHONPATH=/app/backend
EXPOSE 8030

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8030}/health || exit 1

# Run entrypoint
CMD ["/app/entrypoint.sh"]
```

### entrypoint.sh
```bash
#!/bin/bash
set -e

echo "📊 Starting ReportForge Services..."

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
until pg_isready -h reportforge-db -p 5432 -U reportforge 2>/dev/null; do
    sleep 1
done
echo "✅ PostgreSQL is ready"

# Initialize database
echo "🗄️  Initializing database..."
cd /app/backend && python -m app.init_db || echo "⚠️  Database init failed (may already exist)"

# Start FastAPI
PORT=${PORT:-8030}
echo "🌐 Starting ReportForge API Server on port $PORT..."
cd /app/backend && exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level info
```

### .env.example
```bash
# Database
DATABASE_URL=postgresql://reportforge:reportforge_password@reportforge-db:5432/reportforge
POSTGRES_PASSWORD=reportforge_password

# Authentication
SECRET_KEY=your-secret-key-here-change-in-production
MAGIC_LINK_EXPIRY_MINUTES=15
SESSION_EXPIRY_DAYS=30

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@infocert.it
SMTP_PASSWORD=
SMTP_FROM=ReportForge <noreply@infocert.it>

# Application
APP_NAME=ReportForge
APP_URL=https://reportforge.brainaihub.tech
DEBUG=false
ENVIRONMENT=production

# PDF
PDF_BRAND_COLOR=#0066CC
```

---

## 🚀 Deployment Procedure

### Prerequisites on Droplet
- ✅ Docker & Docker Compose installed
- ✅ `proxy-nginx` container running (SNI router)
- ✅ `proxy-nginx_proxy-network` network exists
- ✅ SSL certificates in `swissknife_ssl-data` volume
- ✅ Git repository cloned to `/opt/reportforge`
- ✅ `.env` file configured with production secrets

### Deployment Steps

1. **SSH into Droplet**
   ```bash
   ssh root@10.135.215.172
   cd /opt/reportforge
   ```

2. **Run deploy.sh**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh --force  # Skip confirmations
   ```

3. **What deploy.sh Does**
   - Backs up `.env` file
   - Pulls latest code from GitHub (`git reset --hard origin/main`)
   - Restores `.env` file (preserves secrets)
   - Builds Docker image: `docker compose build`
   - Stops old containers: `docker compose down`
   - Starts new containers: `docker compose up -d`
   - Waits 15s for health check
   - Validates backend health: `curl http://localhost:8030/health`
   - Shows success message with logs commands

4. **Verify Deployment**
   ```bash
   # Check container status
   docker compose ps
   
   # All should be "healthy"
   docker logs reportforge-backend --tail 50
   docker logs reportforge-nginx --tail 50
   
   # Check database tables
   docker exec reportforge-db psql -U reportforge -d reportforge -c '\dt'
   
   # Should show 19 tables
   ```

5. **Test Endpoints**
   ```bash
   # Health check
   curl http://localhost:8030/health
   # → {"status": "healthy"}
   
   # API docs
   curl http://localhost:8030/docs
   # → FastAPI Swagger UI (HTML)
   
   # Public URL (through proxy-nginx)
   curl https://reportforge.brainaihub.tech/health
   # → Should work once nginx config is complete
   ```

---

## 🗄️ Database Schema

### Created Tables (19 total)
```sql
-- Authentication
users, magic_links, user_sessions

-- Projects & Team
projects, team_members, clients, project_team, project_clients
project_activities, project_stakeholders, stakeholders, project_costs

-- Financial
subscriptions, subscription_transactions, revenue_one_time

-- Reports
reports, report_versions, report_projects, report_executive_summary
```

### Sample Query
```bash
# Connect to database
docker exec -it reportforge-db psql -U reportforge -d reportforge

# List tables
\dt

# Describe table
\d users

# Query
SELECT * FROM users;
```

---

## 🔍 Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs reportforge-backend

# Common issues:
# 1. DATABASE_URL wrong hostname → Fix in .env (use reportforge-db)
# 2. Import errors in init_db.py → Check model imports match actual classes
# 3. Postgres not ready → entrypoint.sh handles this with pg_isready
```

### Database Connection Failed
```bash
# Test postgres connectivity
docker exec reportforge-backend pg_isready -h reportforge-db -p 5432 -U reportforge

# Check if containers on same network
docker network inspect proxy-nginx_proxy-network

# Should see reportforge-backend, reportforge-db, reportforge-nginx
```

### Health Check Failing
```bash
# Test health endpoint
docker exec reportforge-backend curl -f http://localhost:8030/health

# Check if uvicorn is running
docker exec reportforge-backend ps aux | grep uvicorn

# Check if port is listening
docker exec reportforge-backend netstat -tlnp | grep 8030
```

### Deploy Script Permission Denied
```bash
chmod +x deploy.sh entrypoint.sh
git update-index --chmod=+x deploy.sh entrypoint.sh
```

---

## 📦 Git Workflow

### Making Changes
```bash
# Local development
cd /workspace/reportforge
# ... make changes ...
git add -A
git commit -m "Description

Co-authored-by: openhands <openhands@all-hands.dev>"
git push origin main
```

### Deploying Changes
```bash
# On droplet
cd /opt/reportforge
./deploy.sh --force

# Script will:
# - Pull latest code
# - Preserve .env secrets
# - Rebuild + restart containers
```

---

## 🔐 Security Notes

### Sensitive Files (NOT in Git)
- `.env` - Production secrets
- `logs/*.log` - Application logs
- `.env.backup.*` - Deploy script backups

### Gitignore Essentials
```
.env
.env.backup.*
logs/
__pycache__/
*.pyc
.DS_Store
```

---

## 📊 Current Status

**Deployment**: ✅ SUCCESSFUL  
**Containers**: All 3 healthy  
**Database**: 19 tables created  
**Network**: Single `proxy-network` architecture  
**DNS**: `reportforge-db` resolution working  
**Init Pattern**: `init_db.py` with `Base.metadata.create_all()` working  
**Entrypoint**: `pg_isready` wait + init + uvicorn working  

**Public URL**: ✅ https://reportforge.brainaihub.tech (HTTPS WORKING!)  
**Internal API**: ✅ http://localhost:8030 (working)  
**Health Check**: ✅ `GET /health` → 200 OK  
**API Docs**: ✅ `GET /api/docs` → FastAPI Swagger UI  
**SSL Certificate**: ✅ Valid Let's Encrypt cert (expires 2026-04-08)  

---

## 🔐 HTTPS / SSL Configuration

### SSL Certificate Setup (Completed ✅)

**Certificate Generated**: 2026-01-08  
**Domain**: reportforge.brainaihub.tech  
**Provider**: Let's Encrypt  
**Expiry**: 2026-04-08  
**Location**: `/etc/letsencrypt/live/reportforge.brainaihub.tech/`

### Nginx HTTPS Configuration

**File**: `nginx/conf.d/reportforge.brainaihub.tech.conf`

Key configuration blocks:

1. **HTTP Server (Port 80)**: 
   - Handles ACME challenges for certbot renewal
   - Redirects all traffic to HTTPS
   - Keeps `/health` endpoint accessible on HTTP

2. **HTTPS Server (Port 443)**:
   - SSL/TLS certificates from `/etc/letsencrypt/live/reportforge.brainaihub.tech/`
   - HTTP/2 enabled
   - Security headers (HSTS, X-Frame-Options, etc.)
   - Proxies all requests to backend:8030

### Docker Volumes for SSL

**docker-compose.yml** mounts (following TrustyVault pattern):
```yaml
volumes:
  - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
  - ./nginx/conf.d:/etc/nginx/conf.d:ro
  - swissknife_ssl-data:/etc/letsencrypt:ro
  - swissknife_certbot-webroot:/var/www/certbot
```

### SNI Routing via proxy-nginx

**Configuration**: `/opt/proxy-nginx/nginx/nginx.conf`

Stream block maps SNI hostname to backend:
```nginx
map $ssl_preread_server_name $backend {
    reportforge.brainaihub.tech    reportforge-nginx:443;
    # ... other services
}

server {
    listen 443;
    ssl_preread on;
    proxy_pass $backend;
}
```

**Important**: After adding new SNI entries, reload proxy-nginx:
```bash
docker exec proxy-nginx nginx -s reload
```

### SSL Verification Commands

```bash
# Test certificate validity
curl -v https://reportforge.brainaihub.tech/health 2>&1 | grep "subject:"
# → subject: CN=reportforge.brainaihub.tech

# Test expiry date
curl -v https://reportforge.brainaihub.tech/health 2>&1 | grep "expire date:"
# → expire date: Apr  8 08:00:07 2026 GMT

# Test TLS version
curl -v https://reportforge.brainaihub.tech/health 2>&1 | grep "SSL connection"
# → SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384
```

---

## 🎯 Development Roadmap

### ✅ PHASE 1: Infrastructure & Design (COMPLETED)

**Task 1-13**: Basic Infrastructure Setup
- ✅ Docker setup (FastAPI + PostgreSQL + Nginx)
- ✅ Database schema (19 tables)
- ✅ HTTPS/SSL configuration
- ✅ Domain migration to reportforge.brainaihub.tech
- ✅ Health check endpoints

**Task 14-23**: Frontend Branding & Login Page
- ✅ Login page HTML/CSS with Tailwind
- ✅ Official Tinexta InfoCert logo integration
- ✅ ReportForge branding (#0072CE blue)
- ✅ Responsive design
- ✅ Magic Link login form UI
- ✅ **CRITICAL FIX**: Logo file deployment issue resolved
  - **Issue**: SVG file showed "Access Denied" XML error instead of logo
  - **Root Cause**: Docker build cached old file, `git pull` didn't update container
  - **Solution**: Used `docker cp` to inject correct logo directly into running container
  - **Files Fixed**: `frontend/static/assets/tinexta-logo-official.svg`
  - **Commit**: 37e673c - "Use official Tinexta InfoCert logo from TrustyVault"

---

### 🔄 PHASE 2: Authentication System (IN PROGRESS)

**Task 24**: Implement Magic Link Backend (2-3 hours)
1. **Email Service Implementation**
   - Configure AWS SES client with boto3
   - Create HTML email template (Jinja2)
   - Implement `email_service.send_magic_link()`
   - Add email logging for debugging
   
2. **Magic Link Generation**
   - Create `/api/auth/request-magic-link` POST endpoint
   - Validate email domain (@infocert.it only)
   - Generate secure token (secrets.token_urlsafe(32))
   - Store token in `magic_links` table with 15min expiry
   - Send email with token link
   
3. **Token Verification**
   - Create `/api/auth/verify` GET endpoint
   - Validate token existence and expiry
   - Create/update user record
   - Generate session token (30 days)
   - Store in `user_sessions` table
   - Set httponly cookie
   - Redirect to dashboard

**Files to Modify**:
```
backend/app/services/email_service.py     # NEW: Email sending logic
backend/app/api/auth.py                   # NEW: Auth endpoints
backend/app/templates/email_magic_link.html  # NEW: Email template
backend/app/models/user.py                # EXISTING: User, MagicLink, UserSession
backend/app/main.py                       # UPDATE: Register auth router
```

**Environment Variables Required** (.env):
```bash
AWS_ACCESS_KEY_ID=AKIAXCYNJR3PTEZMNKKU
AWS_SECRET_ACCESS_KEY=BL/dFzoUubluz5kz4HkrYl6BUhpZ0BfXj3prNF9QC21b
AWS_REGION=eu-west-1
SES_SENDER_EMAIL=noreply@brainaihub.tech
SECRET_KEY=<generate-random-key>
MAGIC_LINK_EXPIRY_MINUTES=15
SESSION_EXPIRY_DAYS=30
```

**Testing Checklist**:
- [ ] Email arrives within 30 seconds
- [ ] Magic link format: `https://reportforge.brainaihub.tech/auth/verify?token=...`
- [ ] Token expires after 15 minutes
- [ ] Invalid token returns 401 error
- [ ] Valid token creates user and session
- [ ] Session cookie persists for 30 days
- [ ] Second login reuses existing user

---

### 🏗️ PHASE 3: Complete API Implementation (8-10 hours)

**Task 25**: Projects API (3 hours)
- `POST /api/projects` - Create new project
- `GET /api/projects` - List all projects (with pagination)
- `GET /api/projects/{id}` - Get single project details
- `PUT /api/projects/{id}` - Update project info
- `DELETE /api/projects/{id}` - Soft delete project
- **Models**: Project, TeamMember, Client, ProjectActivity

**Task 26**: Financial Data API (3 hours)
- `POST /api/subscriptions` - Add subscription revenue
- `POST /api/revenue/onetime` - Add one-time revenue
- `GET /api/subscriptions` - List all subscriptions
- `PUT /api/subscriptions/{id}` - Update subscription
- `DELETE /api/subscriptions/{id}` - Delete subscription
- **Models**: Subscription, RevenueOneTime

**Task 27**: Clients API (2 hours)
- `POST /api/clients` - Create client
- `GET /api/clients` - List all clients
- `PUT /api/clients/{id}` - Update client
- **Models**: Client, ClientContact

**Task 28**: Reports API (2 hours)
- `GET /api/reports` - List all report versions
- `POST /api/reports/generate` - Generate new monthly report
- `GET /api/reports/{id}/pdf` - Download PDF
- **Models**: ReportVersion

**Shared Requirements**:
- Authentication middleware (check session cookie)
- Authorization (user can only access their division's data)
- Input validation (Pydantic schemas)
- Error handling (404, 403, 400, 500)
- Database transactions
- Audit logging (created_by, updated_by)

---

### 🎨 PHASE 4: Dashboard Frontend (10-12 hours)

**Task 29**: Dashboard Layout (2 hours)
- Responsive sidebar navigation
- Top bar with user profile
- Logout button
- Mobile menu toggle
- Active route highlighting

**Task 30**: Projects Management Page (3 hours)
- Projects table with filters/search
- Add new project modal
- Edit project modal
- Delete confirmation
- Team members inline editing
- Client selection dropdown

**Task 31**: Financial Data Entry Page (3 hours)
- Subscriptions table
- One-time revenue table
- Inline editing with validation
- Add/Edit forms
- Date pickers
- Currency formatting

**Task 32**: Report Preview & Generation (2 hours)
- Report history table
- Generate report button
- PDF preview iframe
- Download PDF button
- Status indicators (generating, ready)

**Task 33**: Settings Page (2 hours)
- User profile editing
- Email preferences
- Report templates management
- Division settings

**Technology Stack**:
- HTML/CSS with Tailwind CSS
- Vanilla JavaScript (Alpine.js optional)
- Fetch API for backend calls
- Client-side form validation
- Toast notifications

---

### 📄 PHASE 5: PDF Generation Engine (6-8 hours)

**Task 34**: PPTX Data Extraction (2 hours)
- Parse existing `template.pptx` with python-pptx
- Extract layout/structure information
- Map PPTX content to database fields
- Document data mapping in spreadsheet

**Task 35**: HTML Template Creation (3 hours)
- Convert PPTX design to HTML/CSS
- Use Jinja2 templating
- Match Tinexta InfoCert branding exactly
- Include charts (Chart.js to SVG)
- Tables with proper formatting
- Page breaks for PDF

**Task 36**: WeasyPrint Integration (2 hours)
- Configure WeasyPrint with fonts
- Render HTML to PDF
- Handle images and logos
- Test page layouts
- Optimize file size

**Task 37**: Report Generator Service (1 hour)
- Create `ReportGeneratorService`
- Query all data for date range
- Populate Jinja2 template
- Generate PDF bytes
- Save to `ReportVersion` table
- Return download link

---

### 🧪 PHASE 6: Testing & Polish (4-6 hours)

**Task 38**: Integration Testing (2 hours)
- Test full user flow (login → add data → generate report)
- Test edge cases (empty data, large datasets)
- Test concurrent users
- Load testing (10+ users)

**Task 39**: Error Handling & UX (2 hours)
- User-friendly error messages
- Loading states
- Empty states
- Validation feedback
- Success notifications

**Task 40**: Documentation (2 hours)
- User guide (Italian)
- Admin guide
- API documentation (OpenAPI)
- Deployment guide updates

---

### 🚀 PHASE 7: Production Deployment (2 hours)

**Task 41**: Pre-launch Checklist
- [ ] All environment variables set
- [ ] Database backup configured
- [ ] SSL certificates renewed
- [ ] Email sending tested
- [ ] Monitoring/logging enabled
- [ ] Error alerting configured

**Task 42**: User Training
- Demo session with PM
- Walkthrough of all features
- Q&A session
- Feedback collection

**Task 43**: Launch & Support
- Soft launch to PM only
- Monitor for issues
- Collect feedback
- Iterate on UX improvements

---

## 📊 Effort Estimation Summary

| Phase | Tasks | Estimated Hours | Status |
|-------|-------|----------------|--------|
| Phase 1: Infrastructure | 1-23 | 20 hours | ✅ DONE |
| Phase 2: Authentication | 24 | 3 hours | 🔄 NEXT |
| Phase 3: API | 25-28 | 10 hours | ⏳ TODO |
| Phase 4: Dashboard | 29-33 | 12 hours | ⏳ TODO |
| Phase 5: PDF Engine | 34-37 | 8 hours | ⏳ TODO |
| Phase 6: Testing | 38-40 | 6 hours | ⏳ TODO |
| Phase 7: Launch | 41-43 | 2 hours | ⏳ TODO |
| **TOTAL** | **43 tasks** | **61 hours** | **38% complete** |

---

## 🎯 Immediate Next Steps (Priority Order)

1. **✅ VERIFY**: Logo displays correctly on https://reportforge.brainaihub.tech/
2. **START Task 24**: Implement Magic Link authentication backend (3 hours)
   - Configure AWS SES
   - Create email template
   - Build auth endpoints
   - Test email flow
3. **START Task 25**: Build Projects CRUD API (3 hours)
4. **START Task 29**: Build dashboard layout (2 hours)

---

## 📚 References

- **TrustyVault**: `/opt/trustyvault` - Working reference implementation
- **GitHub Repo**: https://github.com/ilvolodel/reportforge
- **Docker Docs**: https://docs.docker.com/compose/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/

---

## 📧 Amazon SES Configuration (Production)

**Service**: Amazon Simple Email Service (SES)  
**Region**: eu-west-1 (Ireland)  
**Domain**: brainaihub.tech  
**Updated**: 2026-01-08

### SMTP Credentials

```bash
# Email Server
SES_SMTP_HOST=email-smtp.eu-west-1.amazonaws.com

# Ports Available
SES_SMTP_PORT=587                    # STARTTLS (recommended)
# Alternative ports: 25, 2587 (STARTTLS) or 465, 2465 (TLS Wrapper)

# Authentication
SES_SMTP_USERNAME=AKIAXCYNJR3PTEZMNKKU
SES_SMTP_PASSWORD=BL/dFzoUubluz5kz4HkrYl6BUhpZ0BfXj3prNF9QC21b

# AWS API Credentials (for boto3)
AWS_ACCESS_KEY_ID=AKIAXCYNJR3PTEZMNKKU
AWS_SECRET_ACCESS_KEY=BL/dFzoUubluz5kz4HkrYl6BUhpZ0BfXj3prNF9QC21b
AWS_REGION=eu-west-1

# Sender Configuration
SES_SENDER_EMAIL=noreply@brainaihub.tech
SES_SENDER_NAME=ReportForge
```

### Environment Variables (.env)

Add to `/opt/reportforge/.env`:

```bash
# Amazon SES Email Configuration
AWS_ACCESS_KEY_ID=AKIAXCYNJR3PTEZMNKKU
AWS_SECRET_ACCESS_KEY=BL/dFzoUubluz5kz4HkrYl6BUhpZ0BfXj3prNF9QC21b
AWS_REGION=eu-west-1
SES_SMTP_HOST=email-smtp.eu-west-1.amazonaws.com
SES_SMTP_PORT=587
SES_SENDER_EMAIL=noreply@brainaihub.tech
SES_SENDER_NAME=ReportForge

# Magic Link Configuration
MAGIC_LINK_SUBJECT=Your ReportForge Magic Link
MAGIC_LINK_EXPIRY_MINUTES=15
```

### Domain Verification

**Status**: ✅ Verified (by user)  
**Domain**: brainaihub.tech  
**Email**: noreply@brainaihub.tech

**DNS Records** (already configured by user):
- Domain verification TXT record
- DKIM CNAME records (3x)
- SPF record (optional but recommended)

### Python Dependencies

```txt
# requirements.txt
boto3==1.34.28          # AWS SDK for Python
botocore==1.34.28       # AWS SDK core
```

### Usage Example

```python
from app.services.email_service import email_service

# Send magic link
success = email_service.send_magic_link(
    to_email="user@infocert.it",
    magic_link="https://reportforge.brainaihub.tech/auth/verify?token=abc123"
)
```

### Email Template (HTML)

- **Branding**: Tinexta InfoCert colors (#0072CE)
- **CTA Button**: Access Dashboard
- **Expiry Notice**: 15 minutes
- **Footer**: ReportForge by Tinexta InfoCert

### Testing

```bash
# Test email sending
docker-compose exec backend python -c "
from app.services.email_service import email_service
result = email_service.send_magic_link(
    'test@example.com',
    'https://reportforge.brainaihub.tech/auth/verify?token=test123'
)
print(f'Email sent: {result}')
"
```

### SES Limits

**Sandbox Mode**: 200 emails/day  
**Production Mode**: Request limit increase via AWS Support

**Important**: If SES account is in sandbox, you must verify recipient emails before sending.

---

**Maintained by**: OpenHands AI  
**For**: INFOCERT ReportForge Project  
**Contact**: ilvolodel@ilvolodel
