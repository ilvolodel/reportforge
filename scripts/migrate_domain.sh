#!/bin/bash

OLD_DOMAIN="reportforge.bitsync.it"
NEW_DOMAIN="reportforge.brainaihub.tech"

echo "🔄 ReportForge Domain Migration"
echo "================================"
echo "FROM: $OLD_DOMAIN"
echo "TO:   $NEW_DOMAIN"
echo ""

# 1. Update repository files
echo "📝 Updating repository files..."

# .env
sed -i "s|$OLD_DOMAIN|$NEW_DOMAIN|g" .env

# nginx config
cd nginx/conf.d
mv ${OLD_DOMAIN}.conf ${NEW_DOMAIN}.conf 2>/dev/null || true
sed -i "s|$OLD_DOMAIN|$NEW_DOMAIN|g" ${NEW_DOMAIN}.conf
cd ../..

# deploy.sh
sed -i "s|$OLD_DOMAIN|$NEW_DOMAIN|g" deploy.sh

# Documentation
find . -name "*.md" -type f -exec sed -i "s|$OLD_DOMAIN|$NEW_DOMAIN|g" {} \;

echo "✅ Repository files updated"

# 2. Commit changes
echo ""
echo "💾 Committing changes..."
git add -A
git commit -m "Migrate domain from $OLD_DOMAIN to $NEW_DOMAIN

- Update all configuration files
- Update documentation
- Update nginx configs
- Update .env variables

Co-authored-by: openhands <openhands@all-hands.dev>"

git push origin main

echo "✅ Changes committed and pushed"
echo ""
echo "⚠️  MANUAL STEPS REQUIRED:"
echo "1. Configure DNS A record for $NEW_DOMAIN"
echo "2. Wait 5-10 minutes for DNS propagation"
echo "3. Run: ./scripts/update_droplet.sh"
echo "4. Configure Amazon SES"
