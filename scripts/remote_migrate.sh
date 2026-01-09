#!/bin/bash

# Remote Database Migration Script
# Executes migration on production server via SSH

set -e

HOST="root@10.135.215.172"
PASSWORD="Fr3qu3nc1."
PROJECT_DIR="/opt/reportforge"

echo "🗄️  ReportForge Remote Database Migration"
echo "=========================================="
echo ""
echo "Target: $HOST"
echo "Project: $PROJECT_DIR"
echo ""

# Create migration SQL in a heredoc
MIGRATION_SQL=$(cat <<'EOSQL'
DROP TABLE IF EXISTS report_versions CASCADE;
DROP TABLE IF EXISTS report_executive_summary CASCADE;
DROP TABLE IF EXISTS report_project_snapshots CASCADE;
DROP TABLE IF EXISTS report_templates CASCADE;
DROP TABLE IF EXISTS reports CASCADE;
EOSQL
)

echo "📋 Migration will:"
echo "   - Drop old reports tables"
echo "   - Restart backend to recreate with new schema"
echo "   - Verify new tables exist"
echo ""

# Execute migration via SSH
echo "🔐 Connecting to production server..."
echo "$MIGRATION_SQL" | sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$HOST" "
    echo '🔄 Pulling latest code...'
    cd $PROJECT_DIR
    git pull
    
    echo '📊 Dropping old tables...'
    docker exec -i reportforge-db psql -U reportforge -d reportforge
    
    echo '🔄 Restarting backend...'
    docker compose restart backend
    
    echo '⏳ Waiting for backend startup...'
    sleep 5
    
    echo '✅ Verifying new tables...'
    docker exec reportforge-db psql -U reportforge -d reportforge -c '\dt report*'
    
    echo ''
    echo '🎉 Migration complete!'
"

echo ""
echo "✅ Done! Test the API:"
echo "   curl https://reportforge.brainaihub.tech/api/reports/templates"
echo ""
