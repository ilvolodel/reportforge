# 🔄 Database Migration Instructions

## Current Situation

The Reports API has been fully developed with enhanced models, but the database schema is **outdated**.

**Problem:** 
- Old `reports` table exists without new columns (name, period_start, period_end, etc.)
- API returns 500 errors when trying to create reports

**Solution:** 
Drop old tables and let SQLAlchemy recreate them with the new schema.

---

## 🚀 Quick Migration (Recommended)

### Option 1: One-Command Migration

```bash
# SSH to production server
ssh root@10.135.215.172
# Password: Fr3qu3nc1.

# Navigate to project directory
cd /opt/reportforge

# Pull latest code (includes migration scripts)
git pull

# Run migration with SQL file
docker exec -i reportforge-db psql -U reportforge -d reportforge < migrate_reports_schema.sql

# Restart backend to recreate tables
docker compose restart backend

# Wait 5 seconds
sleep 5

# Verify tables were recreated
docker exec reportforge-db psql -U reportforge -d reportforge -c '\dt report*'
```

---

### Option 2: Interactive Migration with Script

```bash
# SSH to production
ssh root@10.135.215.172

# Go to project
cd /opt/reportforge

# Pull latest code
git pull

# Run helper script
bash scripts/migrate_db.sh
# Type 'yes' when prompted
```

---

### Option 3: Manual Step-by-Step

```bash
# 1. SSH to server
ssh root@10.135.215.172

# 2. Connect to database
docker exec -it reportforge-db psql -U reportforge -d reportforge

# 3. Drop old tables (copy-paste this SQL)
DROP TABLE IF EXISTS report_versions CASCADE;
DROP TABLE IF EXISTS report_executive_summary CASCADE;
DROP TABLE IF EXISTS report_project_snapshots CASCADE;
DROP TABLE IF EXISTS report_templates CASCADE;
DROP TABLE IF EXISTS reports CASCADE;

# 4. Exit psql
\q

# 5. Restart backend
cd /opt/reportforge
docker compose restart backend

# 6. Verify (after 5 seconds)
docker exec reportforge-db psql -U reportforge -d reportforge -c '\dt report*'
```

---

## 🧪 Testing After Migration

### 1. Test Templates API

```bash
# Create a template
curl -X POST https://reportforge.brainaihub.tech/api/reports/templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Report Standard",
    "description": "Template completo con tutte le sezioni",
    "is_default": true,
    "config": {
      "include_executive_summary": true,
      "include_pipeline": true,
      "include_team_overview": true
    }
  }'

# Expected: JSON response with template created (id: 1)
```

### 2. Test Reports API

```bash
# Create a report
curl -X POST https://reportforge.brainaihub.tech/api/reports/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Report Dicembre 2024",
    "period_start": "2024-12-01",
    "period_end": "2024-12-31",
    "template_id": 1,
    "project_ids": [1]
  }'

# Expected: JSON response with report created including project snapshots
```

### 3. List Reports

```bash
curl https://reportforge.brainaihub.tech/api/reports/
# Expected: Array with created reports
```

---

## 📋 New Database Schema

After migration, these tables will exist:

### `reports`
```sql
- id (serial, primary key)
- name (varchar 255) -- NEW
- description (text) -- NEW
- period_start (date) -- NEW
- period_end (date) -- NEW
- status (varchar 20) -- NEW: 'draft' or 'final'
- template_config (jsonb) -- NEW
- pdf_path (varchar 500)
- pdf_generated_at (timestamp)
- created_by (integer, fk users)
- created_at (timestamp)
- updated_at (timestamp)
```

### `report_project_snapshots`
```sql
- id (serial, primary key)
- report_id (integer, fk reports)
- project_id (integer, fk projects)
- name, type, status, description, dates
- capex_revenue, subscription_revenue
- capex_saving, subscription_saving
- total_costs
- team (jsonb) -- Array of team members
- stakeholders (jsonb)
- clients (jsonb)
- activities (jsonb)
- costs_breakdown (jsonb)
- notes (text)
- created_at, updated_at
```

### `report_templates`
```sql
- id (serial, primary key)
- name (varchar 255)
- description (text)
- is_default (boolean)
- config (jsonb) -- Template configuration
- created_by (integer, fk users)
- created_at, updated_at
```

### `report_executive_summary`
```sql
- id (serial, primary key)
- report_id (integer, fk reports, unique)
- total_projects (integer)
- total_revenue (decimal 15,2)
- total_costs (decimal 15,2)
- total_saving (decimal 15,2)
- active_subscriptions (integer)
- key_highlights (text)
- risks_and_issues (text)
- created_at, updated_at
```

### `report_versions`
```sql
- id (serial, primary key)
- report_id (integer, fk reports)
- version_number (integer)
- pdf_path (varchar 500)
- changes_summary (text)
- created_by (integer, fk users)
- created_at (timestamp)
```

---

## ⚠️ Important Notes

**Data Loss:** This migration will drop ALL existing reports data. Since we're in early development, this is acceptable.

**Production Safety:** For future migrations with real data, use Alembic migrations instead of dropping tables.

**Backup (Optional):** If you want to backup existing data:
```bash
docker exec reportforge-db pg_dump -U reportforge reportforge > backup_before_migration.sql
```

---

## 🎯 Next Steps After Migration

1. ✅ Verify Reports API works (run tests above)
2. 📝 Update PROJECT_STATE.md to mark migration as complete
3. 🎨 Start building PDF template (Task 27)
4. 🖥️ Start building frontend for Projects CRUD (Task 28)

---

## 🐛 Troubleshooting

### Problem: Tables not recreated after restart

**Solution:**
```bash
# Check backend logs
docker logs reportforge-backend --tail 50

# Look for SQLAlchemy errors
# If tables weren't created, check if models are imported correctly
```

### Problem: Still getting 500 errors

**Solution:**
```bash
# Verify table structure
docker exec reportforge-db psql -U reportforge -d reportforge -c '\d reports'

# Should show ALL new columns including: name, period_start, period_end, status, etc.
```

### Problem: Foreign key errors

**Solution:**
```bash
# Ensure cascade drop worked
docker exec reportforge-db psql -U reportforge -d reportforge -c "
SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename LIKE 'report%';
"

# If old tables still exist, drop manually one by one
```

---

**Status:** 🟡 Migration pending - needs manual execution on production server

**Estimated Time:** 5 minutes

**Risk Level:** LOW (development phase, no production data)
