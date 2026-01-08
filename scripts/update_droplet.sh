#!/bin/bash

NEW_DOMAIN="reportforge.brainaihub.tech"
DROPLET_IP="10.135.215.172"
DROPLET_USER="root"
DROPLET_PASS="Fr3qu3nc1."

echo "🚀 Updating Droplet Configuration"
echo "=================================="

# 1. Update proxy-nginx
echo "📝 Updating proxy-nginx..."
sshpass -p "$DROPLET_PASS" ssh -o StrictHostKeyChecking=no $DROPLET_USER@$DROPLET_IP << 'EOF'
    sed -i "s|reportforge.bitsync.it|reportforge.brainaihub.tech|g" /opt/proxy-nginx/nginx/nginx.conf
    cd /opt/proxy-nginx
    docker compose restart nginx
    echo "✅ Proxy updated and restarted"
EOF

# 2. Generate SSL certificate
echo ""
echo "🔒 Generating SSL certificate..."
sshpass -p "$DROPLET_PASS" ssh -o StrictHostKeyChecking=no $DROPLET_USER@$DROPLET_IP << EOF
    cd /opt/reportforge
    docker compose stop nginx
    
    # Stop proxy to free port 80
    cd /opt/proxy-nginx
    docker compose stop nginx
    
    # Generate certificate
    certbot certonly --standalone \
        -d $NEW_DOMAIN \
        --email admin@brainaihub.tech \
        --agree-tos \
        --non-interactive
    
    # Restart all
    docker compose start nginx
    cd /opt/reportforge
    docker compose start nginx
    
    echo "✅ SSL certificate generated"
EOF

# 3. Deploy new version
echo ""
echo "📦 Deploying new version..."
cd /workspace/reportforge
bash deploy.sh

echo ""
echo "✅ Migration complete!"
echo ""
echo "🔗 New URL: https://$NEW_DOMAIN"
echo ""
echo "⚠️  Next: Configure Amazon SES"
