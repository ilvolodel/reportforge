# 📊 ReportForge - Project State Documentation

> **Last Updated:** 2026-01-09  
> **Version:** 0.5.1 (PDF Generation API Integrated)  
> **Status:** 🟢 In Development - PDF Generation Working, Frontend CRUD Next

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Infrastructure & Deployment](#infrastructure--deployment)
3. [Technology Stack](#technology-stack)
4. [Database Schema](#database-schema)
5. [API Endpoints](#api-endpoints)
6. [Current Development Status](#current-development-status)
7. [Common Operations](#common-operations)
8. [Known Issues & Solutions](#known-issues--solutions)
9. [Next Steps](#next-steps)

---

## 🎯 Project Overview

### Problem Statement
**User:** PM/Operations manager at INFOCERT (Rome, Italy)  
**Pain Point:** Monthly report creation for division activities is:
- Time-consuming and manual
- Error-prone (easy to forget updates)
- Based on PowerPoint templates that need constant editing

### Solution
**ReportForge** - A web dashboard for progressive data entry that automatically generates professional PDF reports with a fixed layout.

### Key Requirements
✅ **Modular/Configurable** - Users select which sections to include  
✅ **Editable Snapshots** - All data editable in report, saves to DB  
✅ **Template System** - Save configurations for reuse ("Report Standard", "Report Executive", etc.)  
✅ **Report Versioning** - View/edit/copy old reports  
✅ **Financial Structure** - CAPEX (one-time) + OPEX/Subscription (recurring) for both revenue and saving  
✅ **InfoCert Branding** - Official Tinexta/InfoCert corporate identity

### NOT Requirements
❌ Not copying existing PPTX structure - improving and simplifying it  
❌ Not a PPTX editor - generating PDFs from structured data  

---

## 🏗️ Infrastructure & Deployment

### Production Environment

**Domain:** https://reportforge.brainaihub.tech  
**IP Address:** 161.35.214.46 (DigitalOcean Droplet)  
**SSH Access:** root@10.135.215.172 (password: `Fr3qu3nc1.`)

**Deploy Location:** `/opt/reportforge`  
**Deploy Method:** Docker Compose

**GitHub Repository:** https://github.com/ilvolodel/reportforge  
**Branch:** main

### Services Architecture

```
┌─────────────────────────────────────────────┐
│  Nginx Reverse Proxy (Port 80/443)         │
│  - HTTPS with Let's Encrypt                 │
│  - Proxies to backend:8030                  │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Backend Container (FastAPI)                │
│  - Port: 8030                               │
│  - Serves API + Static Frontend             │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  PostgreSQL Container                       │
│  - Port: 5432 (internal)                    │
│  - Database: reportforge                    │
│  - User: reportforge                        │
│  - Password: reportforge123                 │
└─────────────────────────────────────────────┘
```

### Email Service (AWS SES)

**SMTP Endpoint:** email-smtp.eu-west-1.amazonaws.com:587  
**Region:** eu-west-1  
**From Email:** reportforge@brainaihub.tech  
**Credentials:** Stored in `/opt/reportforge/.env`

### Test Users

- daniele.castellari.ext@infocert.it
- filippo.savarese@infocert.it

---

## 🛠️ Technology Stack

### Backend
- **Framework:** FastAPI 0.104+
- **ORM:** SQLAlchemy 2.0+
- **Database:** PostgreSQL 15
- **Authentication:** Magic Link (passwordless email)
- **PDF Generation:** WeasyPrint (planned)
- **PPTX Parsing:** python-pptx (planned)
- **Validation:** Pydantic v2

### Frontend
- **Framework:** Vanilla JavaScript (no framework)
- **Styling:** Tailwind CSS 3.4+
- **UI Components:** Custom components with InfoCert branding
- **HTTP Client:** Fetch API

### DevOps
- **Containerization:** Docker + Docker Compose
- **Web Server:** Nginx
- **SSL/TLS:** Let's Encrypt (Certbot)
- **Process Manager:** Uvicorn (in container)

### Branding
- **Primary Color:** #0072CE (InfoCert Blue)
- **Dark Blue:** #005a9e
- **Light Blue:** #e6f3fb
- **Logos:** Official Tinexta/InfoCert logos

---

## 🗄️ Database Schema

### Current State (as of 2026-01-09)

**⚠️ IMPORTANT:** The database schema is currently OUTDATED. The models have been updated but migrations haven't been run.

#### User Management
```sql
users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
)

magic_links (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
)

user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
)
```

#### Projects Module
```sql
projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50), -- 'internal', 'external'
    status VARCHAR(50), -- 'planning', 'active', 'on_hold', 'completed', 'cancelled'
    description TEXT,
    start_date DATE,
    end_date DATE,
    budget DECIMAL(15, 2),
    total_revenue DECIMAL(15, 2), -- Calculated
    total_costs DECIMAL(15, 2), -- Calculated
    capex_revenue DECIMAL(15, 2), -- One-time revenue
    subscription_revenue DECIMAL(15, 2), -- Recurring revenue
    capex_saving DECIMAL(15, 2), -- One-time saving
    subscription_saving DECIMAL(15, 2), -- Recurring saving
    notes TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
)

stakeholders (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(255), -- 'Customer Care', 'Sales', 'Marketing', etc.
    company VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
)

project_stakeholders (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    stakeholder_id INTEGER REFERENCES stakeholders(id) ON DELETE CASCADE
)

clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
)

project_clients (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE
)

team_members (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(255),
    email VARCHAR(255),
    department VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
)

project_team (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    team_member_id INTEGER REFERENCES team_members(id) ON DELETE CASCADE,
    role_in_project VARCHAR(255)
)

project_activities (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50), -- 'planned', 'in_progress', 'completed', 'blocked'
    planned_date DATE,
    completed_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
)

project_costs (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    category VARCHAR(255) NOT NULL, -- 'labor', 'infrastructure', 'software', 'other'
    description TEXT,
    amount DECIMAL(15, 2) NOT NULL,
    date DATE,
    created_at TIMESTAMP DEFAULT NOW()
)
```

#### Revenue Module
```sql
revenue_one_time (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    description TEXT,
    amount DECIMAL(15, 2) NOT NULL,
    invoice_date DATE,
    payment_date DATE,
    status VARCHAR(50), -- 'pending', 'invoiced', 'paid'
    created_at TIMESTAMP DEFAULT NOW()
)

subscriptions (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    monthly_amount DECIMAL(15, 2) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    status VARCHAR(50), -- 'active', 'cancelled', 'paused'
    created_at TIMESTAMP DEFAULT NOW()
)

subscription_transactions (
    id SERIAL PRIMARY KEY,
    subscription_id INTEGER REFERENCES subscriptions(id) ON DELETE CASCADE,
    amount DECIMAL(15, 2) NOT NULL,
    transaction_date DATE NOT NULL,
    period_start DATE,
    period_end DATE,
    status VARCHAR(50), -- 'pending', 'completed', 'failed'
    created_at TIMESTAMP DEFAULT NOW()
)
```

#### Reports Module (⚠️ NEEDS MIGRATION)

**Current Model (in code, NOT in DB yet):**

```sql
reports (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'draft', 'final'
    template_config JSONB NOT NULL, -- Configuration from template
    pdf_path VARCHAR(500),
    pdf_generated_at TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
)

report_project_snapshots (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES reports(id) ON DELETE CASCADE,
    project_id INTEGER REFERENCES projects(id),
    -- Project snapshot (editable copy)
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50),
    status VARCHAR(50),
    description TEXT,
    start_date DATE,
    end_date DATE,
    
    -- Financial snapshot
    capex_revenue DECIMAL(15, 2),
    subscription_revenue DECIMAL(15, 2),
    capex_saving DECIMAL(15, 2),
    subscription_saving DECIMAL(15, 2),
    total_costs DECIMAL(15, 2),
    
    -- Snapshot data (JSONB)
    team JSONB, -- Array of team members
    stakeholders JSONB, -- Array of stakeholders
    clients JSONB, -- Array of clients
    activities JSONB, -- Array of activities
    costs_breakdown JSONB, -- Detailed costs
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
)

report_executive_summary (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES reports(id) ON DELETE CASCADE,
    total_projects INTEGER,
    total_revenue DECIMAL(15, 2),
    total_costs DECIMAL(15, 2),
    total_saving DECIMAL(15, 2),
    active_subscriptions INTEGER,
    key_highlights TEXT,
    risks_and_issues TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
)

report_versions (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES reports(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    pdf_path VARCHAR(500),
    changes_summary TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
)

report_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT false,
    config JSONB NOT NULL, -- Template configuration
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
)
```

**✅ Current DB State:** All report tables migrated successfully with new enhanced schema (as of 2026-01-09)

---

## 🔌 API Endpoints

### Authentication (`/api/auth/`)
- `POST /request-magic-link` - Request magic link via email
- `GET /verify-magic-link?token=...` - Verify magic link
- `POST /logout` - Logout current user
- `GET /me` - Get current user info

### Projects (`/api/projects/`)
- `GET /` - List all projects
- `POST /` - Create new project
- `GET /{id}` - Get project details
- `PUT /{id}` - Update project
- `DELETE /{id}` - Delete project

### Clients (`/api/clients/`)
- `GET /` - List all clients
- `POST /` - Create new client
- `GET /{id}` - Get client details
- `PUT /{id}` - Update client
- `DELETE /{id}` - Delete client

### Team Members (`/api/team/`)
- `GET /members` - List all team members
- `POST /members` - Create new team member
- `GET /members/{id}` - Get team member details
- `PUT /members/{id}` - Update team member
- `DELETE /members/{id}` - Delete team member

### Stakeholders (`/api/stakeholders/`)
- `GET /` - List all stakeholders
- `POST /` - Create new stakeholder
- `GET /{id}` - Get stakeholder details
- `PUT /{id}` - Update stakeholder
- `DELETE /{id}` - Delete stakeholder

### Subscriptions (`/api/subscriptions/`)
- `GET /` - List all subscriptions
- `POST /` - Create new subscription
- `GET /{id}` - Get subscription details
- `PUT /{id}` - Update subscription
- `DELETE /{id}` - Delete subscription
- `GET /{id}/transactions` - Get subscription transactions
- `POST /{id}/transactions` - Add transaction

### Revenue (`/api/revenue/`)
- `GET /one-time` - List all one-time revenue
- `POST /one-time` - Create one-time revenue
- `GET /one-time/{id}` - Get one-time revenue details
- `PUT /one-time/{id}` - Update one-time revenue
- `DELETE /one-time/{id}` - Delete one-time revenue

### Reports (`/api/reports/`) ⚠️ **Recently Added - Needs DB Migration**

#### Templates
- `GET /templates` - List all report templates
- `POST /templates` - Create new template
- `GET /templates/{id}` - Get template details
- `PUT /templates/{id}` - Update template
- `DELETE /templates/{id}` - Delete template

#### Reports CRUD
- `GET /` - List all reports
- `POST /` - Create new report (from template or custom config)
- `GET /{id}` - Get report details with all snapshots
- `PUT /{id}` - Update report metadata
- `DELETE /{id}` - Delete report
- `POST /{id}/copy` - Copy existing report with new period

#### Project Snapshots
- `GET /{id}/projects` - Get all project snapshots in report
- `PUT /{id}/projects/{snapshot_id}` - Update project snapshot (editable)
- `DELETE /{id}/projects/{snapshot_id}` - Remove project from report

#### Executive Summary
- `GET /{id}/executive-summary` - Get executive summary
- `PUT /{id}/executive-summary` - Update executive summary
- `POST /{id}/executive-summary/recalculate` - Recalculate totals from snapshots

#### PDF Generation
- `POST /{id}/generate-pdf` - Generate PDF from report (⚠️ NOT IMPLEMENTED YET)

---

## 📊 Current Development Status

### ✅ Completed (Tasks 1-25)

1. **Infrastructure Setup**
   - DigitalOcean droplet provisioned
   - Docker + Docker Compose configured
   - Nginx reverse proxy with HTTPS
   - Let's Encrypt SSL certificates
   - Domain DNS configured

2. **Backend Foundation**
   - FastAPI application structure
   - PostgreSQL database setup
   - SQLAlchemy ORM models
   - Pydantic validation schemas
   - Environment configuration

3. **Authentication System**
   - Magic link (passwordless) authentication
   - Email sending via AWS SES
   - Session management with cookies
   - User model and permissions

4. **Database Models**
   - Users, Sessions, Magic Links
   - Projects with full financial tracking (CAPEX/OPEX structure)
   - Clients, Stakeholders, Team Members
   - Project Activities and Costs
   - Subscriptions and One-time Revenue
   - **Reports Models (defined, not migrated)**

5. **CRUD APIs**
   - Projects API (full CRUD)
   - Clients API (full CRUD)
   - Team Members API (full CRUD)
   - Stakeholders API (full CRUD)
   - Subscriptions API (full CRUD + transactions)
   - Revenue API (one-time revenue CRUD)
   - **Reports API (created, not deployed properly)**

6. **Frontend (Basic)**
   - Login page with magic link flow
   - Dashboard layout with InfoCert branding
   - Navigation structure
   - Tailwind CSS setup

7. **Branding**
   - InfoCert color scheme implemented
   - Official Tinexta/InfoCert logos
   - Corporate identity applied

### ✅ Recently Completed (Tasks 26, 26a, 27)

**Reports API Implementation** ✅
- ✅ Created report models (Report, ReportProjectSnapshot, ReportTemplate, etc.)
- ✅ Created report schemas (Pydantic)
- ✅ Built comprehensive Reports API with all endpoints
- ✅ Implemented snapshot creation and editing
- ✅ Implemented report copying functionality
- ✅ API registered in main.py
- ✅ Code committed and pushed to GitHub
- ✅ **Database migration executed successfully**
- ✅ **API tested and verified working in production**

**Database Migration (Task 26a)** ✅
- ✅ Created remote_migrate.py script with Paramiko
- ✅ Executed migration: Dropped old tables
- ✅ Backend restarted, new schema recreated by SQLAlchemy
- ✅ Verified 6 new tables created correctly
- ✅ Tested API endpoints working correctly

**PDF Template System (Task 27)** ✅
- ✅ Created WeasyPrint-compatible HTML/CSS template system
- ✅ Base template (base.html) with Jinja2 conditionals
- ✅ Comprehensive CSS styles.css with InfoCert branding (colors, typography, layouts)
- ✅ 8 modular sections created:
  - cover_page.html - Title, logo, period, metadata
  - executive_summary.html - KPIs, revenue/saving comparison, benefits, stakeholders
  - projects_overview.html - Project list table with status badges
  - project_detail.html - Detailed project info with activities, deliverables
  - team_stakeholders.html - Team members and stakeholders tables
  - financial_overview.html - Summary cards, breakdown by client
  - revenue_details.html - Subscriptions, one-time revenue, savings details
  - back_cover.html - Contacts and document info
- ✅ Test script (test_pdf_generation.py) with comprehensive mock data
- ✅ Local PDF generation tested successfully (49.5 KB output)
- ✅ Automated deployment script (deploy_production.py) created
- ✅ Code deployed to production with Docker rebuild
- ✅ Updated WeasyPrint to v67.0 and Jinja2 to v3.1.6

**PDF Generation API Integration (Task 27a)** ✅
- ✅ Created PDFGenerationService (backend/app/services/pdf_service.py)
  - fetch_report_data(): Loads all report data from database
  - generate_pdf(): Renders HTML with Jinja2 and converts to PDF with WeasyPrint
  - generate_html_preview(): Returns HTML for debugging
- ✅ Updated Reports API (backend/app/api/reports.py)
  - POST /api/reports/{id}/generate-pdf: Generate and download PDF
  - GET /api/reports/{id}/preview-html: HTML preview endpoint
- ✅ Fixed database model field access (4 iterations)
  - Report.template_config instead of template_id
  - ReportProjectSnapshot individual fields instead of snapshot_data
  - Subscription.annual_value and description (no name field)
  - TeamMember.full_name instead of name
  - Stakeholder simplified fields
- ✅ Tested in production: Successfully generated 4.1KB PDF + HTML preview
- ✅ Deployed to production (commit: e3ff90b)

### ❌ Pending (Tasks 28-34)

28. **Frontend: Projects CRUD Page** 🔄 NEXT
    - List view with filters and search
    - Create/Edit forms with validation
    - Financial data entry (CAPEX/OPEX)
    - Team/Stakeholders/Clients assignment
    - Activities timeline

29. **Frontend: Clients, Team, Stakeholders CRUD**
    - Separate management pages for each entity
    - List views with search
    - Create/Edit modals or forms

30. **Frontend: Subscriptions & Revenue CRUD**
    - Subscriptions list and management
    - Transaction tracking
    - One-time revenue management
    - Financial overview dashboard

31. **Frontend: Reports Management Page**
    - Reports list (filterable by period, status)
    - Create report wizard (select template, period, projects)
    - Quick actions (view, edit, copy, generate PDF)
    - Status indicators (draft/final)

32. **Frontend: Report Editor with Live Preview**
    - Section-by-section editing
    - Project snapshots editing (inline)
    - Executive summary editing
    - Live preview of PDF layout
    - Save as draft / Finalize report

33. **Implement PDF Generation**
    - WeasyPrint integration
    - HTML template rendering
    - CSS for print layout
    - Asset handling (logos, charts)
    - PDF storage and retrieval

34. **End-to-End Testing**
    - Complete user workflow test
    - Create projects with all data
    - Create report from template
    - Edit snapshots
    - Generate PDF
    - Verify PDF output quality

---

## ⚙️ Common Operations

### 🚀 Deployment Workflow

```bash
# 1. Commit and push changes
cd /workspace/reportforge
git add -A
git commit -m "feat: your description"
git push

# 2. SSH to production server
ssh root@10.135.215.172
# Password: Fr3qu3nc1.

# 3. Pull latest code
cd /opt/reportforge
git pull

# 4. Rebuild and restart containers
docker compose build backend  # Only if backend code changed
docker compose up -d backend

# 5. Check logs
docker logs reportforge-backend --tail 50

# 6. Verify health
curl http://localhost:8030/health
```

### 🗄️ Database Operations

```bash
# Connect to database
ssh root@10.135.215.172
docker exec -it reportforge-db psql -U reportforge -d reportforge

# Common queries
\dt                                    # List tables
\d table_name                          # Describe table
SELECT * FROM users;                   # Query data
SELECT * FROM reports;                 # Check reports table

# Backup database
docker exec reportforge-db pg_dump -U reportforge reportforge > backup.sql

# Restore database
cat backup.sql | docker exec -i reportforge-db psql -U reportforge -d reportforge
```

### 🐛 Debugging

```bash
# View backend logs
docker logs reportforge-backend -f

# View database logs
docker logs reportforge-db -f

# View nginx logs
docker logs reportforge-nginx -f

# Execute commands in backend container
docker exec -it reportforge-backend bash
python -c "from app.api import reports; print('OK')"

# Check database schema
docker exec reportforge-db psql -U reportforge -d reportforge -c '\d reports'

# Test API endpoints locally
curl -X POST https://reportforge.brainaihub.tech/api/reports/templates \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "is_default": false, "config": {}}'
```

### 🔄 Database Migration (AUTOMATED)

**✅ Solution Implemented:** `scripts/remote_migrate.py`

This Python script uses Paramiko to automatically:
1. Connect to production server via SSH
2. Pull latest code
3. Drop old tables
4. Restart backend (auto-creates new tables)
5. Verify migration success

**Usage:**
```bash
cd /workspace/reportforge
python3 scripts/remote_migrate.py
```

**Status:** ✅ Executed successfully on 2026-01-09

---

## ⚠️ Known Issues & Solutions

### ✅ RESOLVED: Reports API 500 Error

**Was:** Database schema mismatch causing 500 errors
**Resolution:** Executed remote_migrate.py on 2026-01-09
**Status:** ✅ All Reports API endpoints working correctly

### Current Issues

**None** - All critical blockers resolved!

---

### Issue 2: Model Import Errors After Refactoring

**Symptom:**
```
ImportError: cannot import name 'ReportProject' from 'app.models.report'
```

**Cause:** Model was renamed to `ReportProjectSnapshot` but `__init__.py` had old import.

**Solution:** Already fixed in commit `9cfdf05`.

**Status:** ✅ RESOLVED

---

### Issue 3: Docker Container Not Picking Up New Code

**Symptom:** New files (like `reports.py`) not found in container.

**Cause:** Docker layer caching - new files not copied into image.

**Solution:** Always run `docker compose build backend` after adding new files.

**Status:** ✅ RESOLVED

---

## 🎯 Next Steps

### Immediate (Current Sprint)

1. **✅ DONE: Fix Database Schema & Test Reports API**
   - Executed remote_migrate.py successfully
   - Tested all endpoints working correctly
   - Templates, Reports, Snapshots all functional

2. **Design PDF Template Structure** (Task 27 - NEXT PRIORITY)
   - Review user's PPTX template (available: template.pptx)
   - Design HTML/CSS layout with InfoCert branding
   - Make sections modular (show/hide based on template_config)
   - Use WeasyPrint-compatible CSS
   - ETA: 4-6 hours

### Short Term (This Week)

4. **Implement PDF Generation**
   - Install WeasyPrint dependencies
   - Create Jinja2 templates for report sections
   - Implement PDF generation endpoint
   - Test with real data
   - ETA: 4-6 hours

5. **Build Frontend: Projects CRUD**
   - Design UI/UX for projects page
   - Implement list view with filters
   - Create/edit forms
   - Financial data entry (CAPEX/OPEX)
   - Team assignment
   - ETA: 6-8 hours

### Medium Term (Next 2 Weeks)

6. **Build Frontend: Reports Management**
   - Reports list page
   - Create report wizard
   - Report editor with sections
   - Live PDF preview
   - ETA: 8-10 hours

7. **Complete All CRUD Frontends**
   - Clients, Team Members, Stakeholders
   - Subscriptions & Revenue
   - ETA: 6-8 hours

### Long Term (Month 1)

8. **Polish & Production Ready**
   - User feedback integration
   - Bug fixes and refinements
   - Performance optimization
   - Documentation
   - Training materials
   - ETA: Ongoing

---

## 📝 Development Notes

### Code Organization

```
reportforge/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints (auth, projects, reports, etc.)
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── core/          # Config, security, database
│   │   ├── utils/         # Utilities (email, etc.)
│   │   ├── init_db.py     # Database initialization
│   │   └── main.py        # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/         # Jinja2 templates
├── docker-compose.yml
├── entrypoint.sh
└── PROJECT_STATE.md       # This file
```

### Naming Conventions

- **Models:** PascalCase (e.g., `ReportProjectSnapshot`)
- **Tables:** snake_case (e.g., `report_project_snapshots`)
- **API Endpoints:** kebab-case (e.g., `/api/reports/templates`)
- **Schema Fields:** snake_case (e.g., `period_start`)
- **Python Variables:** snake_case (e.g., `project_id`)
- **JavaScript Variables:** camelCase (e.g., `projectId`)

### Financial Data Structure

All projects follow this structure:

**Revenue:**
- `capex_revenue`: One-time revenue (upfront payment)
- `subscription_revenue`: Recurring monthly revenue

**Saving:**
- `capex_saving`: One-time cost savings
- `subscription_saving`: Recurring monthly savings

**Costs:**
- `total_costs`: Sum of all project costs
- Breakdown: `labor`, `infrastructure`, `software`, `other`

### Report Snapshots Philosophy

When a report is created:
1. User selects projects to include
2. System creates **snapshots** of project data (copy)
3. Snapshots are **editable** (independent from original)
4. Snapshot changes can **optionally sync back** to original project
5. This allows historical reports to remain unchanged even if projects evolve

---

## 🎓 Learning Resources

### FastAPI
- Docs: https://fastapi.tiangolo.com/
- Key concepts: Dependency injection, Pydantic validation, async/await

### SQLAlchemy 2.0
- Docs: https://docs.sqlalchemy.org/en/20/
- Key concepts: ORM, relationships, JSONB columns

### WeasyPrint
- Docs: https://weasyprint.org/
- Key concepts: HTML to PDF, CSS for print, @page rules

### Tailwind CSS
- Docs: https://tailwindcss.com/
- Key concepts: Utility-first CSS, responsive design

---

## 📞 Support & Contacts

**User Contact:** (INFOCERT PM - details in test users)  
**Developer:** AI Assistant (OpenHands)  
**Repository Issues:** https://github.com/ilvolodel/reportforge/issues  

---

**END OF PROJECT STATE DOCUMENT**

*This document should be updated regularly as the project evolves.*
