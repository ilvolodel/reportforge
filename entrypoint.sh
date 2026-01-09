#!/bin/bash
# ReportForge - Container Entrypoint Script

set -e

echo "📊 Starting ReportForge Services..."
echo ""

# Display git commit if available
if [ -f /app/.git_commit ]; then
    COMMIT=$(cat /app/.git_commit)
    echo "📌 Git Commit: $COMMIT"
fi

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
until pg_isready -h reportforge-db -p 5432 -U reportforge 2>/dev/null; do
    sleep 1
done
echo "✅ PostgreSQL is ready"
echo ""

# Initialize database (create tables if not exists)
echo "🗄️  Initializing database..."
cd /app/backend && python -m app.init_db || echo "⚠️  Database init failed (may already exist)"
echo ""

# Start FastAPI server
PORT=${PORT:-8030}
echo "🌐 Starting ReportForge API Server on port $PORT..."
echo "   - API endpoints: /api/"
echo "   - Health check: /health"
echo "   - Docs: /docs"
cd /app/backend && exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level info
