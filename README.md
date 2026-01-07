# ReportForge 🔥

**Monthly Report Generator Dashboard for INFOCERT**

Automated monthly reporting system with progressive data entry and PDF generation.

## 🎯 Features

- **Magic Link Authentication** - Passwordless, email-based login
- **Project Management** - Track internal, partner, and client projects
- **Financial Tracking** - Revenue, savings, costs (CAPEX + subscriptions)
- **Team & Stakeholder Management** - Organize project teams and stakeholders
- **Complete Versioning** - Full snapshot history before every save
- **PDF Export** - Professional reports with INFOCERT branding
- **Multi-user Support** - Multiple users with single-user workflow

## 🏗️ Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15
- **PDF Generation**: WeasyPrint
- **Frontend**: Tailwind CSS + Alpine.js
- **Deployment**: Docker Compose + Nginx

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- SMTP credentials for magic link emails

### Local Development

```bash
# Clone repository
git clone https://github.com/ilvolodel/reportforge.git
cd reportforge

# Copy environment file
cp .env.example .env

# Edit .env with your settings (especially SMTP credentials)
nano .env

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Access application
open http://localhost:8080
```

### Production Deployment (Droplet)

```bash
# SSH to droplet
ssh root@10.135.215.172

# Clone repository to /opt/reportforge
cd /opt
git clone https://github.com/ilvolodel/reportforge.git
cd reportforge

# Configure environment
cp .env.example .env
nano .env  # Update with production values

# Deploy
chmod +x deploy.sh
sudo ./deploy.sh

# Application will be available at:
# https://reportforge.bitsync.it
```

## 📋 Database Schema

### Master Tables
- `users` - User authentication
- `magic_links` - Passwordless auth tokens
- `projects` - Core project entities
- `stakeholders` - Customer Care, Sales, Marketing
- `clients` - NORMA, ASL CUNEO, Casadei
- `team_members` - J. Cotrina, F. Savarese

### Financial Tables
- `project_costs` - INTERNAL/VENDOR/INFRASTRUCTURE
- `revenue_one_time` - CAPEX revenue/saving
- `subscriptions` - Annual recurring forecast
- `subscription_transactions` - Monthly actuals

### Report Tables
- `reports` - Monthly report snapshots
- `report_projects` - Projects in each report
- `report_versions` - Full versioning (JSONB)

## 🔧 Configuration

Key environment variables in `.env`:

```bash
# Database
POSTGRES_PASSWORD=your_secure_password

# Authentication
SECRET_KEY=your_secret_key_here
MAGIC_LINK_EXPIRY_MINUTES=15
SESSION_EXPIRY_DAYS=30

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@infocert.it
SMTP_PASSWORD=your_smtp_password
SMTP_FROM=ReportForge <noreply@infocert.it>

# Application
APP_URL=https://reportforge.bitsync.it
```

## 🐳 Docker Services

The application consists of 3 services:

1. **postgres** - PostgreSQL database
2. **backend** - FastAPI application
3. **nginx** - Web server & reverse proxy

## 📦 Project Structure

```
reportforge/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── api/             # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── templates/       # Jinja2 (PDF, email)
│   │   └── utils/           # Utilities
│   ├── alembic/             # Database migrations
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── static/              # CSS, JS, assets
│   └── templates/           # HTML templates
├── nginx/                   # Nginx configuration
├── docker-compose.yml       # Docker services
├── Dockerfile               # Backend container
└── deploy.sh                # Deployment script
```

## 🔐 Security

- Passwordless authentication via magic links
- Session tokens with 30-day expiry
- HTTPS in production (via nginx proxy)
- Environment-based secrets
- PostgreSQL with strong passwords

## 📚 API Documentation

Once running, access:
- Swagger UI: `http://localhost:8080/api/docs`
- ReDoc: `http://localhost:8080/api/redoc`

## 🛠️ Useful Commands

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop all services
docker-compose down

# Database shell
docker-compose exec postgres psql -U reportforge

# Backend shell
docker-compose exec backend bash

# Run migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"
```

## 📝 Development Roadmap

### Phase 1 (Current)
- [x] Database schema design
- [x] Docker infrastructure
- [ ] Alembic migrations
- [ ] Magic link authentication
- [ ] CRUD APIs (projects, team, clients)
- [ ] Basic frontend UI

### Phase 2
- [ ] PDF generation with WeasyPrint
- [ ] PDF import from existing template
- [ ] Versioning system UI
- [ ] Executive summary calculations

### Phase 3
- [ ] Production deployment
- [ ] End-to-end testing
- [ ] Performance optimization

## 🤝 Contributing

This is an internal project for INFOCERT. For questions or issues, contact the development team.

## 📄 License

Private - Internal use only

---

**Built with ❤️ for INFOCERT**
