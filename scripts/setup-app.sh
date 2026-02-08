#!/bin/bash

# ============================================
# InstaGrowth OS - App Setup Script
# Run after install-dependencies.sh
# ============================================

echo "🚀 Setting up InstaGrowth OS Application..."
echo "==========================================="

# Configuration - EDIT THESE
DOMAIN="yourdomain.com"
MONGO_PASSWORD="change_this_secure_password"
JWT_SECRET="your-super-secret-jwt-key-minimum-32-characters-long"
ADMIN_CODE="INSTAGROWTH_ADMIN_2024"

# Exit on error
set -e

cd /var/www/instagrowth

# ============================================
# STEP 1: Setup Backend
# ============================================
echo ""
echo "🔧 Step 1: Setting up Backend..."
cd /var/www/instagrowth/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install emergent integrations
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/

# Create .env file
cat > .env << EOF
MONGO_URL=mongodb://localhost:27017
DB_NAME=instagrowth_db
JWT_SECRET=${JWT_SECRET}
ADMIN_SECRET_CODE=${ADMIN_CODE}
OPENAI_API_KEY=your-openai-key-here
RESEND_API_KEY=your-resend-key-here
SENDER_EMAIL=noreply@${DOMAIN}
FRONTEND_URL=https://${DOMAIN}
EOF

echo "✅ Backend setup complete"

# ============================================
# STEP 2: Setup Frontend
# ============================================
echo ""
echo "🎨 Step 2: Setting up Frontend..."
cd /var/www/instagrowth/frontend

# Install dependencies
yarn install

# Create .env file
cat > .env << EOF
REACT_APP_BACKEND_URL=https://${DOMAIN}
GENERATE_SOURCEMAP=false
EOF

# Build for production
yarn build

echo "✅ Frontend build complete"

# ============================================
# STEP 3: Setup Nginx
# ============================================
echo ""
echo "🌐 Step 3: Configuring Nginx..."

sudo tee /etc/nginx/sites-available/instagrowth > /dev/null << EOF
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};
    
    root /var/www/instagrowth/frontend/build;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 300s;
    }

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/instagrowth /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

echo "✅ Nginx configured"

# ============================================
# STEP 4: Setup PM2
# ============================================
echo ""
echo "⚙️ Step 4: Setting up PM2..."

cat > /var/www/instagrowth/ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'instagrowth-backend',
      cwd: '/var/www/instagrowth/backend',
      script: 'venv/bin/uvicorn',
      args: 'server:app --host 0.0.0.0 --port 8001 --workers 4',
      interpreter: 'none',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
    }
  ]
};
EOF

# Start application
cd /var/www/instagrowth
pm2 start ecosystem.config.js
pm2 save
pm2 startup systemd -u $USER --hp /home/$USER

echo "✅ PM2 configured"

# ============================================
# DONE
# ============================================
echo ""
echo "==========================================="
echo "✅ InstaGrowth OS Setup Complete!"
echo "==========================================="
echo ""
echo "🔐 Next Steps:"
echo "1. Point your domain DNS to this server IP"
echo "2. Run: sudo certbot --nginx -d ${DOMAIN} -d www.${DOMAIN}"
echo "3. Update API keys in /var/www/instagrowth/backend/.env"
echo "4. Restart: pm2 restart instagrowth-backend"
echo ""
echo "📍 URLs:"
echo "- Frontend: http://${DOMAIN}"
echo "- Backend API: http://${DOMAIN}/api/"
echo "- Admin Panel: http://${DOMAIN}/admin-panel/login"
echo ""
echo "🔑 Default Admin:"
echo "- Email: superadmin@instagrowth.com"
echo "- Password: SuperAdmin123!"
echo "- Security Code: ${ADMIN_CODE}"
echo ""
