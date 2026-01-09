#!/bin/bash

# Database Migration Script for ReportForge
# Usage: ./scripts/migrate_db.sh

set -e

echo "🗄️  ReportForge Database Migration"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're on the production server
if [ -d "/opt/reportforge" ]; then
    echo "📍 Running on production server"
    PROJECT_DIR="/opt/reportforge"
else
    echo -e "${YELLOW}⚠️  Not on production server. This script should run on 10.135.215.172${NC}"
    echo "   You can copy this to production with:"
    echo "   scp scripts/migrate_db.sh root@10.135.215.172:/opt/reportforge/"
    exit 1
fi

cd "$PROJECT_DIR"

echo ""
echo "📋 Migration: Drop old reports tables"
echo "   This will:"
echo "   - Drop existing reports, report_versions, report_executive_summary tables"
echo "   - Drop report_project_snapshots, report_templates tables"
echo "   - SQLAlchemy will recreate them with new schema on backend restart"
echo ""
read -p "❓ Continue with migration? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${YELLOW}❌ Migration cancelled${NC}"
    exit 0
fi

echo ""
echo "🔄 Dropping old tables..."

docker exec -i reportforge-db psql -U reportforge -d reportforge <<EOF
-- Drop old reports tables
DROP TABLE IF EXISTS report_versions CASCADE;
DROP TABLE IF EXISTS report_executive_summary CASCADE;
DROP TABLE IF EXISTS report_project_snapshots CASCADE;
DROP TABLE IF EXISTS report_templates CASCADE;
DROP TABLE IF EXISTS reports CASCADE;

-- Verify tables are dropped
\dt report*
EOF

echo ""
echo -e "${GREEN}✅ Old tables dropped successfully${NC}"
echo ""
echo "🔄 Restarting backend to recreate tables..."

docker compose restart backend

echo ""
echo "⏳ Waiting for backend to start..."
sleep 5

echo ""
echo "🔍 Verifying new tables..."

docker exec -i reportforge-db psql -U reportforge -d reportforge <<EOF
\dt report*
EOF

echo ""
echo -e "${GREEN}✅ Migration complete!${NC}"
echo ""
echo "📊 New tables created:"
echo "   - reports (with enhanced schema)"
echo "   - report_project_snapshots (editable project data)"
echo "   - report_templates (reusable configurations)"
echo "   - report_executive_summary (calculated summaries)"
echo "   - report_versions (version history)"
echo ""
echo "🧪 Test the API:"
echo "   curl https://reportforge.brainaihub.tech/api/reports/templates"
echo ""
