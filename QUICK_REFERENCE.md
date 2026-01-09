# ⚡ ReportForge - Quick Reference

> **For when you need info FAST!**

---

## 🔐 Access & Credentials

### Production Server
```
SSH: root@10.135.215.172
Password: Fr3qu3nc1.
```

### Domain
```
https://reportforge.brainaihub.tech
```

### GitHub
```
https://github.com/ilvolodel/reportforge
Branch: main
```

### Database (on production)
```
Host: localhost (inside Docker network)
Database: reportforge
User: reportforge
Password: reportforge123
Port: 5432 (internal only)
```

### Test Users
```
daniele.castellari.ext@infocert.it
filippo.savarese@infocert.it
```

---

## 🚀 Quick Deploy

```bash
# 1. Commit & push locally
git add -A && git commit -m "feat: description" && git push

# 2. SSH to production
ssh root@10.135.215.172
# Password: Fr3qu3nc1.

# 3. Update code
cd /opt/reportforge
git pull

# 4. Rebuild (if needed) and restart
docker compose build backend    # Only if Python code changed
docker compose up -d backend

# 5. Check it worked
docker logs reportforge-backend --tail 30
curl http://localhost:8030/health
```

---

## 🗄️ Database Quick Access

```bash
# Connect to DB
ssh root@10.135.215.172
docker exec -it reportforge-db psql -U reportforge -d reportforge

# Once inside psql:
\dt                     # List all tables
\d reports              # Describe reports table
SELECT * FROM users;    # Query users
\q                      # Exit
```

---

## 🔍 Troubleshooting

### Backend not starting?
```bash
docker logs reportforge-backend --tail 100
docker compose restart backend
```

### Database connection issues?
```bash
docker ps                                  # Check containers running
docker exec reportforge-db psql -U reportforge -d reportforge -c '\dt'
```

### Need to rebuild everything?
```bash
cd /opt/reportforge
docker compose down
docker compose build
docker compose up -d
```

### Check what's listening
```bash
netstat -tulpn | grep LISTEN
curl http://localhost:8030/health
curl http://localhost:8030/api/projects
```

---

## 📝 Important File Locations

### On Production Server
```
/opt/reportforge/                      # Main app directory
/opt/reportforge/.env                  # Environment variables (secrets!)
/opt/reportforge/docker-compose.yml    # Docker services config
/var/lib/docker/volumes/               # Database data (persistent)
```

### In Repository
```
PROJECT_STATE.md                       # 📖 MAIN DOCUMENTATION - Start here!
DEPLOYMENT_GUIDE.md                    # Full deployment procedures
MAINTENANCE_GUIDE.md                   # How to update docs
MIGRATION_INSTRUCTIONS.md              # Database migration guide
QUICK_REFERENCE.md                     # This file!

backend/app/                           # FastAPI application
backend/app/api/                       # API endpoints
backend/app/models/                    # SQLAlchemy models
backend/app/schemas/                   # Pydantic schemas

frontend/templates/                    # HTML templates
frontend/static/                       # CSS, JS, images

scripts/                               # Helper scripts
scripts/remote_migrate.py              # Database migration automation
```

---

## 🎯 Current Status (Quick Look)

**Version:** 0.4.0  
**Status:** 🟢 Backend Complete, Frontend Starting  
**Progress:** 27/34 tasks (79%)

**Completed:**
- ✅ Authentication (magic links)
- ✅ Projects CRUD API
- ✅ Clients, Team, Stakeholders CRUD API
- ✅ Subscriptions & Revenue API
- ✅ **Reports API (full CRUD + snapshots)**
- ✅ Database migration automated

**Next Priority:**
- 🔄 Task 27: PDF Template Design (HTML/CSS with InfoCert branding)
- ⏳ Task 28-32: Frontend Development
- ⏳ Task 33: PDF Generation Implementation
- ⏳ Task 34: End-to-end Testing

**See PROJECT_STATE.md for complete details.**

---

## 🧪 Test API Quickly

```bash
# Health check
curl https://reportforge.brainaihub.tech/health

# Get all projects
curl https://reportforge.brainaihub.tech/api/projects

# Get all reports
curl https://reportforge.brainaihub.tech/api/reports/

# Get report templates
curl https://reportforge.brainaihub.tech/api/reports/templates

# API docs (in browser)
open https://reportforge.brainaihub.tech/docs
```

---

## 📚 Documentation Quick Links

| Need to... | Read this... |
|------------|--------------|
| **Understand full project** | [PROJECT_STATE.md](./PROJECT_STATE.md) (START HERE!) |
| **Deploy changes** | [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) |
| **Migrate database** | [MIGRATION_INSTRUCTIONS.md](./MIGRATION_INSTRUCTIONS.md) |
| **Update documentation** | [MAINTENANCE_GUIDE.md](./MAINTENANCE_GUIDE.md) |
| **Quick reference** | [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) (this file) |
| **Update template** | [.github/UPDATE_TEMPLATE.md](./.github/UPDATE_TEMPLATE.md) |

---

## 🎨 InfoCert Branding

**Colors:**
- Primary Blue: `#0072CE`
- Dark Blue: `#005a9e`
- Light Blue: `#e6f3fb`

**Logos:**
- `frontend/static/assets/infocert-logo.svg`
- `frontend/static/assets/tinexta-logo-official.svg`

---

## ⚙️ Environment Variables

**Key variables in `/opt/reportforge/.env`:**

```bash
# Database
POSTGRES_PASSWORD=reportforge123

# Authentication
SECRET_KEY=your_secret_key_32_chars_long
MAGIC_LINK_EXPIRY_MINUTES=15

# Email (AWS SES)
SMTP_HOST=email-smtp.eu-west-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=<aws_ses_user>
SMTP_PASSWORD=<aws_ses_password>
SMTP_FROM=reportforge@brainaihub.tech

# Application
APP_URL=https://reportforge.brainaihub.tech
```

**⚠️ Don't commit `.env` to Git!** (It's in `.gitignore`)

---

## 🔧 Docker Commands Quick Reference

```bash
# View all containers
docker ps

# View logs
docker logs reportforge-backend --tail 50 -f    # Follow logs
docker logs reportforge-db --tail 50

# Restart services
docker compose restart backend
docker compose restart nginx

# Rebuild
docker compose build backend
docker compose up -d backend

# Stop everything
docker compose down

# Start everything
docker compose up -d

# Execute command in container
docker exec -it reportforge-backend bash        # Get shell
docker exec reportforge-db psql -U reportforge -d reportforge   # DB access
```

---

## 💡 Pro Tips

1. **Always read PROJECT_STATE.md first** - It has everything!
2. **Update docs after major changes** - Use MAINTENANCE_GUIDE.md
3. **Test locally before deploying** - Save time debugging
4. **Check logs after deploy** - Catch errors early
5. **Backup database before migrations** - Safety first!

---

**Last Updated:** 2026-01-09  
**For detailed info, see:** [PROJECT_STATE.md](./PROJECT_STATE.md)
