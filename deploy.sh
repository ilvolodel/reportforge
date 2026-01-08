#!/bin/bash
# ReportForge - Docker Deploy Script
set -e

# Parse arguments
FORCE_DEPLOY=false
if [ "$1" = "--force" ]; then
    FORCE_DEPLOY=true
    echo "🚨 Force deploy mode enabled (skip confirmations)"
fi

echo "📊 Starting ReportForge Deployment..."
echo ""

# Navigate to ReportForge directory
cd /opt/reportforge

# Backup .env file (production config should not be overwritten)
echo "💾 Backing up .env file..."
if [ -f .env ]; then
    cp .env .env.backup.tmp
    echo "✅ .env backed up"
else
    echo "⚠️  No .env file found"
fi
echo ""

# Pull latest code
echo "📥 1/4 Pulling latest code from GitHub..."
git fetch origin

# Check for local changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Local changes detected!"
    echo "Files modified:"
    git status --short
    echo ""

    if [ "$FORCE_DEPLOY" = false ]; then
        read -p "Discard local changes and continue? (yes/no): " CONFIRM
        if [ "$CONFIRM" != "yes" ]; then
            echo "Deploy cancelled. Restore .env manually if needed:"
            echo "  mv .env.backup.tmp .env"
            exit 1
        fi
    else
        echo "⚠️  Force mode: Discarding local changes automatically"
    fi
fi

# Update code
git reset --hard origin/main
echo "✅ Code updated"
echo ""

# Restore .env file
echo "♻️  Restoring .env file..."
if [ -f .env.backup.tmp ]; then
    mv .env.backup.tmp .env
    echo "✅ .env restored"

    # Cleanup old backup files
    find . -maxdepth 1 -name ".env.backup.*" -type f -mtime +7 -delete 2>/dev/null || true
fi
echo ""

# Build Docker image
echo "🔨 2/4 Building Docker image..."
docker compose build
echo "✅ Image built"
echo ""

# Stop and remove old container
echo "🛑 3/4 Stopping old container..."
docker compose down
echo "✅ Container stopped and removed"
echo ""

# Start new container
echo "🚀 4/4 Starting new container..."
docker compose up -d
echo "✅ Container started"
echo ""

# Wait for container to be healthy
echo "⏳ Waiting for container to be healthy..."
sleep 15

# Check health
if docker exec reportforge-backend curl -f http://localhost:8030/health > /dev/null 2>&1; then
    echo "✅ Container is healthy"
    echo ""
    echo "╔════════════════════════════════════════╗"
    echo "║                                        ║"
    echo "║    ✅  REPORTFORGE DEPLOYED!  ✅      ║"
    echo "║                                        ║"
    echo "╚════════════════════════════════════════╝"
    echo ""
    echo "🌐 Services running:"
    echo "   Backend API:    http://localhost:8030"
    echo "   Health check:   /health"
    echo "   API docs:       /docs"
    echo "   Public URL:     https://reportforge.bitsync.it/"
    echo ""
    echo "📋 Logs:"
    echo "   docker logs -f reportforge-backend"
    echo "   docker logs -f reportforge-nginx"
    echo "   docker exec reportforge-backend tail -f /app/logs/*.log"
    echo ""
else
    echo "❌ Deploy failed - health check not responding"
    echo ""
    echo "🔍 Check logs:"
    echo "   docker logs reportforge-backend"
    echo "   docker logs reportforge-nginx"
    exit 1
fi
