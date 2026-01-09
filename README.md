# 📊 ReportForge

**Monthly report generation system for INFOCERT operations.**

Transform manual monthly reporting into an automated, efficient workflow with progressive data entry and professional PDF generation.

---

## 🎯 Quick Links

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **[PROJECT_STATE.md](./PROJECT_STATE.md)** | Complete project documentation & state | Start here! Full context of the project |
| **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** | ⚡ Fast access to credentials, deploy, troubleshooting | Need info FAST! |
| **[MAINTENANCE_GUIDE.md](./MAINTENANCE_GUIDE.md)** | How to keep docs updated | When updating documentation |
| **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** | Production deployment procedures | When deploying to production |
| **[MIGRATION_INSTRUCTIONS.md](./MIGRATION_INSTRUCTIONS.md)** | Database migration guide | When migrating database schema |
| **[.github/UPDATE_TEMPLATE.md](./.github/UPDATE_TEMPLATE.md)** | Quick update template | When completing a task/sprint |

---

## ✨ Features

- 🔐 **Magic Link Authentication** - Passwordless email-based login
- 📁 **Project Management** - Complete CRUD with financial tracking (CAPEX/OPEX)
- 👥 **Team & Stakeholder Management** - Track team members, clients, and stakeholders
- 💰 **Revenue Tracking** - One-time and subscription-based revenue management
- 📊 **Report System** - Create reports with editable snapshots and templates
- 🎨 **InfoCert Branding** - Official Tinexta/InfoCert corporate identity
- 📄 **PDF Generation** - Automated professional report generation (planned)

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database with JSONB support
- **SQLAlchemy** - ORM with full relationship support
- **Pydantic** - Data validation and serialization
- **AWS SES** - Email service for magic links

### Frontend
- **Vanilla JavaScript** - No framework overhead
- **Tailwind CSS** - Utility-first CSS framework
- **InfoCert Design System** - Custom branded components

### DevOps
- **Docker + Docker Compose** - Containerization
- **Nginx** - Reverse proxy with HTTPS
- **Let's Encrypt** - SSL/TLS certificates

---

## 🚀 Quick Start

### For Developers (New to Project)

**Start here to understand the full context:**

```bash
# 1. Read the complete project state
cat PROJECT_STATE.md

# 2. Clone repository
git clone https://github.com/ilvolodel/reportforge.git
cd reportforge

# 3. Read deployment guide for setup
cat DEPLOYMENT_GUIDE.md
```

### For Continuing Development

**When you come back to work on the project:**

```bash
# 1. Check current state (always start here!)
cat PROJECT_STATE.md | head -100

# 2. Pull latest changes
git pull

# 3. Check what needs to be done
# Look at "Current Development Status" and "Next Steps" in PROJECT_STATE.md
```

### For Documentation Updates

**After completing work:**

```bash
# 1. Use the update template
cp .github/UPDATE_TEMPLATE.md /tmp/my_update.md
# Fill it out

# 2. Update PROJECT_STATE.md based on template

# 3. Read maintenance guide for details
cat MAINTENANCE_GUIDE.md
```

---

## 📚 Project Structure

```
reportforge/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── core/              # Config, security
│   │   └── utils/             # Utilities
│   └── requirements.txt
├── frontend/                   # Static frontend
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/             # Jinja2 templates
├── nginx/                      # Nginx configuration
├── scripts/                    # Helper scripts
├── docs/                       # Additional documentation
├── PROJECT_STATE.md           # 🎯 MAIN DOCUMENTATION
├── MAINTENANCE_GUIDE.md       # How to maintain docs
├── DEPLOYMENT_GUIDE.md        # Deployment procedures
├── docker-compose.yml
└── README.md                  # This file
```

---

## 🎓 Documentation System

This project uses a **"Micro-Agent"** documentation system to maintain context across development sessions.

### Key Concept

**PROJECT_STATE.md** serves as a "save point" containing:
- Complete project overview
- Infrastructure details (servers, credentials, domains)
- Database schema (current and planned)
- API endpoints documentation
- Development status and task tracking
- Common operations (deploy, debug, database)
- Known issues and solutions
- Next steps and priorities

### When to Update

| Situation | Action | Document |
|-----------|--------|----------|
| Completed a task | Update status, mark task done | PROJECT_STATE.md |
| Changed infrastructure | Update infrastructure section | PROJECT_STATE.md |
| Added API endpoints | Update API section | PROJECT_STATE.md |
| Changed DB schema | Update database section | PROJECT_STATE.md |
| Found/fixed a bug | Update known issues | PROJECT_STATE.md |
| Changed deployment | Update deployment guide | DEPLOYMENT_GUIDE.md |
| End of sprint | Full review and update | PROJECT_STATE.md |

**See [MAINTENANCE_GUIDE.md](./MAINTENANCE_GUIDE.md) for detailed instructions.**

---

## 🔐 Access Information

**Production:**
- **URL:** https://reportforge.brainaihub.tech
- **Server:** root@10.135.215.172 (password in PROJECT_STATE.md)
- **Deploy Path:** /opt/reportforge

**Test Users:**
- daniele.castellari.ext@infocert.it
- filippo.savarese@infocert.it

**GitHub:** https://github.com/ilvolodel/reportforge

---

## 🎯 Current Status

**Version:** 0.3.0  
**Phase:** Backend Development - Reports API Complete  
**Status:** 🟡 Database migration pending

**Progress:** 26/34 tasks complete (76%)

**Next Up:**
1. Execute database migration (5 min)
2. Test Reports API end-to-end
3. Build PDF template with InfoCert branding
4. Start frontend development

**See PROJECT_STATE.md for complete status.**

---

## 🤝 Contributing

### Workflow

1. **Understand context** - Read PROJECT_STATE.md
2. **Make changes** - Develop features/fixes
3. **Update docs** - Use UPDATE_TEMPLATE.md
4. **Commit** - Use descriptive commit messages
5. **Deploy** - Follow DEPLOYMENT_GUIDE.md
6. **Update PROJECT_STATE** - Keep documentation current

### Commit Message Format

```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

---

## 📞 Support

**Primary Contact:** (See PROJECT_STATE.md for user details)  
**Issues:** https://github.com/ilvolodel/reportforge/issues  
**Documentation Questions:** See MAINTENANCE_GUIDE.md

---

## 📄 License

Internal project for INFOCERT. Not for public distribution.

---

**Remember:** 
- 📖 Always start by reading PROJECT_STATE.md
- 🔄 Keep documentation updated (see MAINTENANCE_GUIDE.md)
- ✅ Mark tasks as complete when done
- 📝 Document important decisions and issues

*Last Updated: 2026-01-09*
