#!/bin/bash

# ReportForge Deployment Script
# Run this script on the droplet to deploy/update the application

set -e

APP_NAME="reportforge"
DEPLOY_DIR="/opt/${APP_NAME}"
REPO_URL="https://github.com/yourusername/reportforge.git"  # Update with actual repo

echo "=== ReportForge Deployment Script ==="
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo: sudo ./deploy.sh"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    exit 1
fi

# Create deploy directory if it doesn't exist
if [ ! -d "$DEPLOY_DIR" ]; then
    echo "Creating deploy directory: $DEPLOY_DIR"
    mkdir -p "$DEPLOY_DIR"
fi

cd "$DEPLOY_DIR"

# If this is first deploy and no files exist, we're starting fresh
if [ ! -f "docker-compose.yml" ]; then
    echo "First time deployment detected"
    echo "Please copy your application files to: $DEPLOY_DIR"
    echo "Then run this script again"
    exit 0
fi

# Pull latest changes (if using git)
# Uncomment if using git deployment
# if [ -d ".git" ]; then
#     echo "Pulling latest changes..."
#     git pull
# fi

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down || true

# Build and start containers
echo "Building and starting containers..."
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be healthy
echo "Waiting for services to start..."
sleep 10

# Check container status
echo ""
echo "=== Container Status ==="
docker-compose ps

# Show logs
echo ""
echo "=== Recent Logs ==="
docker-compose logs --tail=50

echo ""
echo "=== Deployment Complete! ==="
echo "Application URL: https://reportforge.bitsync.it"
echo ""
echo "Useful commands:"
echo "  View logs:        cd $DEPLOY_DIR && docker-compose logs -f"
echo "  Restart:          cd $DEPLOY_DIR && docker-compose restart"
echo "  Stop:             cd $DEPLOY_DIR && docker-compose down"
echo "  Database shell:   cd $DEPLOY_DIR && docker-compose exec postgres psql -U reportforge"
echo "  Backend shell:    cd $DEPLOY_DIR && docker-compose exec backend bash"
echo ""
