#!/bin/bash
# ================================================================
# InstaGrowth OS - Complete AWS Deployment Commands
# GitHub: https://github.com/nikka005/instagrowth.git
# Domain: instagrowth.io
# ================================================================

# ============================================
# STEP 1: CONNECT TO YOUR AWS EC2 SERVER
# ============================================

# Download your .pem key from AWS and run:
chmod 400 your-key.pem
ssh -i "your-key.pem" ubuntu@YOUR_EC2_IP

# ============================================
# STEP 2: UPDATE SYSTEM
# ============================================

sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git vim htop unzip software-properties-common

# ============================================
# STEP 3: INSTALL NODE.JS 20.x
# ============================================

curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g yarn pm2

# Verify
node --version
npm --version

# ============================================
# STEP 4: INSTALL PYTHON 3.11
# ============================================

sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Verify
python3.11 --version

# ============================================
# STEP 5: INSTALL MONGODB 7.0
# ============================================

curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
   sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify
sudo systemctl status mongod

# ============================================
# STEP 6: INSTALL NGINX & CERTBOT
# ============================================

sudo apt install -y nginx certbot python3-certbot-nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# ============================================
# STEP 7: CLONE YOUR GITHUB REPOSITORY
# ============================================

sudo mkdir -p /var/www/instagrowth
sudo chown -R $USER:$USER /var/www/instagrowth
cd /var/www/instagrowth

# Clone your repo
git clone https://github.com/nikka005/instagrowth.git .

# ============================================
# STEP 8: SETUP BACKEND
# ============================================

cd /var/www/instagrowth/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install Emergent Integrations (IMPORTANT - for AI features)
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/

# Create backend .env file
cat > /var/www/instagrowth/backend/.env << 'EOF'
MONGO_URL=mongodb://localhost:27017
DB_NAME=instagrowth_db
JWT_SECRET=your-super-secret-jwt-key-change-this-minimum-32-characters
ADMIN_SECRET_CODE=INSTAGROWTH_ADMIN_2024
OPENAI_API_KEY=your-openai-api-key-here
RESEND_API_KEY=your-resend-api-key-here
SENDER_EMAIL=noreply@instagrowth.io
FRONTEND_URL=https://instagrowth.io
EOF

# Test backend
python -c "from server import app; print('Backend OK')"

# ============================================
# STEP 9: SETUP FRONTEND
# ============================================

cd /var/www/instagrowth/frontend

# Install dependencies
yarn install

# Create frontend .env file
cat > /var/www/instagrowth/frontend/.env << 'EOF'
REACT_APP_BACKEND_URL=https://instagrowth.io
GENERATE_SOURCEMAP=false
EOF

# Build for production
yarn build

# ============================================
# STEP 10: CONFIGURE NGINX
# ============================================

sudo tee /etc/nginx/sites-available/instagrowth > /dev/null << 'EOF'
server {
    listen 80;
    server_name instagrowth.io www.instagrowth.io;
    
    root /var/www/instagrowth/frontend/build;
    index index.html;

    # Frontend
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8001/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
    }

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/instagrowth /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test and reload
sudo nginx -t
sudo systemctl reload nginx

# ============================================
# STEP 11: SETUP PM2 PROCESS MANAGER
# ============================================

# Create PM2 config
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

# Create log directory
sudo mkdir -p /var/log/pm2
sudo chown -R $USER:$USER /var/log/pm2

# Start backend with PM2
cd /var/www/instagrowth
pm2 start ecosystem.config.js
pm2 save
pm2 startup systemd

# ============================================
# STEP 12: SETUP SSL CERTIFICATE (HTTPS)
# ============================================

# Make sure DNS is pointing to your server first!
# A record: instagrowth.io -> YOUR_EC2_IP
# A record: www.instagrowth.io -> YOUR_EC2_IP

sudo certbot --nginx -d instagrowth.io -d www.instagrowth.io

# Test auto-renewal
sudo certbot renew --dry-run

# ============================================
# DEPLOYMENT COMPLETE!
# ============================================

echo ""
echo "=========================================="
echo "✅ InstaGrowth OS Deployed Successfully!"
echo "=========================================="
echo ""
echo "🌐 Website: https://instagrowth.io"
echo "🔧 Admin Panel: https://instagrowth.io/admin-panel/login"
echo ""
echo "🔑 Default Admin Credentials:"
echo "   Email: superadmin@instagrowth.com"
echo "   Password: SuperAdmin123!"
echo "   Security Code: INSTAGROWTH_ADMIN_2024"
echo ""
echo "⚠️ IMPORTANT: Update these in production!"
echo ""
