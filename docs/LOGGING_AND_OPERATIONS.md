# 📊 Logging & Operations Guide

**ReportForge - Operational Documentation**  
Version: 1.0  
Last Updated: 2026-01-08

---

## 🔍 **Accessing Logs**

### **Production Server SSH Access**

```bash
# SSH into production server
ssh root@10.135.215.172
# Password: Fr3qu3nc1.

# Or with sshpass
sshpass -p 'Fr3qu3nc1.' ssh root@10.135.215.172
```

### **Docker Container Logs**

```bash
# View all backend logs
docker logs reportforge-backend

# Follow logs in real-time
docker logs -f reportforge-backend

# Last 100 lines
docker logs reportforge-backend --tail 100

# Logs with timestamps
docker logs reportforge-backend --timestamps

# Logs from last 1 hour
docker logs reportforge-backend --since 1h

# Database logs
docker logs reportforge-db --tail 50

# Nginx logs
docker logs reportforge-nginx --tail 50
```

### **Filter Logs by Keywords**

```bash
# Search for specific email
docker logs reportforge-backend 2>&1 | grep "filippo.savarese"

# Search for errors
docker logs reportforge-backend 2>&1 | grep -i "error"

# Search for authentication events
docker logs reportforge-backend 2>&1 | grep -E "(Magic|auth|login)"

# Search for email sending
docker logs reportforge-backend 2>&1 | grep -E "(📧|SMTP|email)"

# Search for API requests
docker logs reportforge-backend 2>&1 | grep "POST\|GET\|PUT\|DELETE"
```

---

## 📝 **Log Levels & Configuration**

### **Current Logging Setup**

**File:** `backend/app/main.py`

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(name)s - %(message)s'
)
```

### **Log Levels**

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages (current level)
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical failures

### **Module-specific Loggers**

```python
# Email service logs
logger = logging.getLogger(__name__)  # app.services.email_service

# Authentication logs  
logger = logging.getLogger(__name__)  # app.api.auth

# Report generator logs
logger = logging.getLogger(__name__)  # app.services.report_generator
```

---

## 🎯 **Key Log Messages**

### **Authentication Flow**

```
INFO: app.api.auth - Created new user: filippo.savarese@infocert.it
INFO: app.api.auth - 📧 About to send magic link to filippo.savarese@infocert.it
INFO: app.api.auth - 🔗 Magic link URL: https://reportforge.brainaihub.tech/auth/verify?token=...
INFO: app.services.email_service - 🔄 Starting email send process for filippo.savarese@infocert.it
INFO: app.services.email_service - 📧 SMTP Config: email-smtp.eu-west-1.amazonaws.com:587
INFO: app.services.email_service - Connecting to SMTP: email-smtp.eu-west-1.amazonaws.com:587
INFO: app.services.email_service - Sending magic link email to filippo.savarese@infocert.it
INFO: app.services.email_service - ✅ Magic link email sent successfully to filippo.savarese@infocert.it
INFO: app.api.auth - 📬 Email send result: True
INFO: app.api.auth - Magic link sent to filippo.savarese@infocert.it, expires at 2026-01-08 16:00:00
```

### **Login Success**

```
INFO: app.api.auth - User filippo.savarese@infocert.it logged in successfully, session expires at 2026-02-07 15:00:00
```

### **HTTP Requests (Uvicorn)**

```
INFO: 172.19.0.20:39584 - "POST /api/auth/request-magic-link HTTP/1.1" 200 OK
INFO: 172.19.0.20:50676 - "GET /auth/verify?token=... HTTP/1.1" 303 See Other
INFO: 172.19.0.20:50690 - "GET /dashboard HTTP/1.1" 200 OK
```

---

## 🚨 **Troubleshooting Common Issues**

### **Email Not Received**

```bash
# 1. Check backend logs for email sending
docker logs reportforge-backend 2>&1 | grep -E "(📧|email|SMTP)" | tail -20

# 2. Check for SMTP errors
docker logs reportforge-backend 2>&1 | grep -i "smtp.*error"

# 3. Verify environment variables
docker exec reportforge-backend env | grep SMTP
```

**Expected Output:**
```
SMTP_HOST=email-smtp.eu-west-1.amazonaws.com
SMTP_PORT=587
SMTP_USERNAME=AKIAXCYNJR3PTEZMNKKU
SMTP_PASSWORD=BL/dFzoUubluz5kz4HkrYl6BUhpZ0BfXj3prNF9QC21b
SMTP_SENDER_EMAIL=noreply@brainaihub.tech
```

### **Magic Link 404 Error**

```bash
# Check if public router is configured
docker exec reportforge-backend grep -r "public_router" /app/backend/app/

# Should show:
# /app/backend/app/api/auth.py:public_router = APIRouter(tags=["Authentication - Public"])
# /app/backend/app/main.py:app.include_router(auth.public_router)
```

### **Database Connection Issues**

```bash
# Check database container
docker ps | grep reportforge-db

# Check database logs
docker logs reportforge-db --tail 50

# Test connection from backend
docker exec reportforge-backend psql $DATABASE_URL -c "SELECT COUNT(*) FROM users;"
```

---

## 🔧 **Operational Commands**

### **Restart Services**

```bash
cd /opt/reportforge

# Restart single service
docker compose restart backend
docker compose restart nginx
docker compose restart db

# Restart all services
docker compose restart

# Full rebuild and restart
docker compose down
docker compose up -d --build
```

### **View Service Status**

```bash
# Check running containers
docker ps

# Check container health
docker compose ps

# View resource usage
docker stats reportforge-backend reportforge-db reportforge-nginx
```

### **Deploy New Code**

```bash
cd /opt/reportforge

# Pull latest code
git pull origin main

# Rebuild and restart affected services
docker compose build backend
docker compose up -d backend

# Or restart without rebuild (if only Python files changed)
docker compose restart backend
```

### **Database Operations**

```bash
# Access PostgreSQL CLI
docker exec -it reportforge-db psql -U reportforge -d reportforge

# Backup database
docker exec reportforge-db pg_dump -U reportforge reportforge > backup_$(date +%Y%m%d).sql

# Check database size
docker exec reportforge-db psql -U reportforge -d reportforge -c "SELECT pg_size_pretty(pg_database_size('reportforge'));"

# List all users
docker exec reportforge-db psql -U reportforge -d reportforge -c "SELECT email, full_name, last_login_at FROM users;"
```

---

## 📈 **Monitoring & Alerting**

### **Health Check Endpoint**

```bash
# Check service health
curl https://reportforge.brainaihub.tech/health

# Expected response:
{
  "status": "healthy",
  "service": "ReportForge",
  "environment": "production"
}
```

### **Key Metrics to Monitor**

1. **Email Delivery Rate**
   ```bash
   # Count successful email sends (last 100 logs)
   docker logs reportforge-backend --tail 100 | grep "✅ Magic link email sent" | wc -l
   
   # Count failed email sends
   docker logs reportforge-backend --tail 100 | grep "Failed to send" | wc -l
   ```

2. **User Logins**
   ```bash
   # Count login events
   docker logs reportforge-backend | grep "logged in successfully" | wc -l
   
   # Recent logins
   docker logs reportforge-backend | grep "logged in successfully" | tail -10
   ```

3. **API Response Times**
   ```bash
   # Check response codes
   docker logs reportforge-backend | grep -E "(200|303|400|404|500)" | tail -20
   ```

4. **Container Resource Usage**
   ```bash
   docker stats --no-stream reportforge-backend reportforge-db
   ```

---

## 🔐 **Security Logs**

### **Failed Login Attempts**

```bash
# Check for invalid magic links
docker logs reportforge-backend | grep "Invalid Link\|expired\|not found"

# Check for domain validation failures
docker logs reportforge-backend | grep "Only @infocert.it"
```

### **Session Management**

```bash
# Active sessions in database
docker exec reportforge-db psql -U reportforge -d reportforge -c \
  "SELECT user_id, created_at, expires_at FROM user_sessions WHERE is_active=true;"

# Expired sessions
docker exec reportforge-db psql -U reportforge -d reportforge -c \
  "SELECT COUNT(*) FROM user_sessions WHERE is_active=false;"
```

---

## 📊 **Log Rotation & Storage**

### **Current Setup**

Docker automatically rotates logs with these settings (can be configured in `docker-compose.yml`):

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### **Manual Log Cleanup**

```bash
# Clear all Docker logs (CAUTION!)
truncate -s 0 $(docker inspect --format='{{.LogPath}}' reportforge-backend)
truncate -s 0 $(docker inspect --format='{{.LogPath}}' reportforge-db)
truncate -s 0 $(docker inspect --format='{{.LogPath}}' reportforge-nginx)
```

---

## 🛠️ **Useful Aliases**

Add these to your `~/.bashrc` or `~/.zshrc`:

```bash
# ReportForge aliases
alias rf-logs='docker logs reportforge-backend --tail 100 -f'
alias rf-logs-db='docker logs reportforge-db --tail 50 -f'
alias rf-status='cd /opt/reportforge && docker compose ps'
alias rf-restart='cd /opt/reportforge && docker compose restart backend'
alias rf-deploy='cd /opt/reportforge && git pull origin main && docker compose build backend && docker compose up -d backend'
alias rf-health='curl -s https://reportforge.brainaihub.tech/health | jq'
```

---

## 📞 **Support & Escalation**

### **Quick Reference**

- **GitHub Repo**: https://github.com/ilvolodel/reportforge
- **Production URL**: https://reportforge.brainaihub.tech
- **Server IP**: 10.135.215.172
- **Domain**: reportforge.brainaihub.tech → 161.35.214.46

### **Common Issues & Solutions**

| Issue | Command | Expected Fix |
|-------|---------|--------------|
| Email not sending | `docker logs reportforge-backend \| grep SMTP` | Check SMTP credentials in `.env` |
| 404 on magic link | `docker compose restart backend` | Restart backend to load routes |
| Database connection error | `docker compose restart db backend` | Restart database first, then backend |
| Slow response | `docker stats` | Check resource usage |
| SSL certificate expired | `docker exec reportforge-nginx certbot renew` | Renew Let's Encrypt cert |

---

**Last Review**: 2026-01-08  
**Next Review**: 2026-02-08 (monthly)
