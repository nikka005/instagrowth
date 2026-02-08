# 🚀 InstaGrowth OS - AWS Deployment Guide

## Complete deployment instructions for AWS EC2/Ubuntu Server

---

# 📋 TABLE OF CONTENTS

1. [Server Requirements](#server-requirements)
2. [AWS EC2 Setup](#aws-ec2-setup)
3. [Server Configuration](#server-configuration)
4. [Install Dependencies](#install-dependencies)
5. [Database Setup (MongoDB)](#database-setup)
6. [Backend Deployment](#backend-deployment)
7. [Frontend Deployment](#frontend-deployment)
8. [Nginx Configuration](#nginx-configuration)
9. [SSL Certificate (HTTPS)](#ssl-certificate)
10. [Environment Variables](#environment-variables)
11. [Process Manager (PM2)](#process-manager)
12. [Domain Configuration](#domain-configuration)
13. [Monitoring & Logs](#monitoring-logs)
14. [Troubleshooting](#troubleshooting)

---

# 1. SERVER REQUIREMENTS

## Minimum Specs
- **OS**: Ubuntu 22.04 LTS (recommended)
- **RAM**: 4GB minimum (8GB recommended)
- **CPU**: 2 vCPU minimum
- **Storage**: 30GB SSD
- **Recommended Instance**: t3.medium or t3.large

## Required Ports
- 22 (SSH)
- 80 (HTTP)
- 443 (HTTPS)
- 3000 (Frontend - internal)
- 8001 (Backend - internal)
- 27017 (MongoDB - internal only)

---

# 2. AWS EC2 SETUP

## Step 1: Launch EC2 Instance

```bash
# AWS Console Steps:
# 1. Go to EC2 Dashboard
# 2. Click "Launch Instance"
# 3. Select: Ubuntu Server 22.04 LTS
# 4. Instance Type: t3.medium
# 5. Configure Security Group (see below)
# 6. Create or select key pair
# 7. Launch instance
```

## Step 2: Configure Security Group

```bash
# Inbound Rules:
# - SSH (22) from Your IP
# - HTTP (80) from Anywhere (0.0.0.0/0)
# - HTTPS (443) from Anywhere (0.0.0.0/0)

# Outbound Rules:
# - All traffic to Anywhere
```

## Step 3: Connect to Server

```bash
# Download your .pem key file
chmod 400 your-key.pem

# Connect via SSH
ssh -i "your-key.pem" ubuntu@your-ec2-public-ip
```

---

# 3. SERVER CONFIGURATION

## Update System

```bash
# Update package list
sudo apt update

# Upgrade all packages
sudo apt upgrade -y

# Install essential tools
sudo apt install -y curl wget git vim htop unzip software-properties-common
```

## Set Timezone

```bash
sudo timedatectl set-timezone UTC
```

## Create App User (Optional but recommended)

```bash
sudo adduser instagrowth
sudo usermod -aG sudo instagrowth
```

---

# 4. INSTALL DEPENDENCIES

## Install Node.js 20.x

```bash
# Add NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

# Install Node.js
sudo apt install -y nodejs

# Verify installation
node --version  # Should show v20.x.x
npm --version   # Should show 10.x.x

# Install Yarn globally
sudo npm install -g yarn
```

## Install Python 3.11

```bash
# Add deadsnakes PPA
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Set Python 3.11 as default (optional)
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Verify
python3 --version  # Should show 3.11.x
```

## Install Nginx

```bash
sudo apt install -y nginx

# Start and enable
sudo systemctl start nginx
sudo systemctl enable nginx

# Verify
sudo systemctl status nginx
```

## Install Certbot (for SSL)

```bash
sudo apt install -y certbot python3-certbot-nginx
```

---

# 5. DATABASE SETUP (MongoDB)

## Install MongoDB 7.0

```bash
# Import MongoDB GPG key
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
   sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Update and install
sudo apt update
sudo apt install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify
sudo systemctl status mongod
mongosh --eval "db.version()"
```

## Secure MongoDB (Production)

```bash
# Connect to MongoDB
mongosh

# Create admin user
use admin
db.createUser({
  user: "instagrowth_admin",
  pwd: "YOUR_SECURE_PASSWORD_HERE",
  roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
})

# Create app database and user
use instagrowth_db
db.createUser({
  user: "instagrowth_app",
  pwd: "YOUR_APP_PASSWORD_HERE",
  roles: [ { role: "readWrite", db: "instagrowth_db" } ]
})

exit
```

```bash
# Enable authentication - edit MongoDB config
sudo nano /etc/mongod.conf

# Add/modify these lines:
# security:
#   authorization: enabled

# Restart MongoDB
sudo systemctl restart mongod
```

---

# 6. BACKEND DEPLOYMENT

## Clone Repository

```bash
# Create app directory
sudo mkdir -p /var/www/instagrowth
sudo chown -R $USER:$USER /var/www/instagrowth
cd /var/www/instagrowth

# Clone your repo (or upload files)
git clone https://github.com/YOUR_USERNAME/instagrowth-os.git .

# Or upload via SCP
# scp -i your-key.pem -r ./app/* ubuntu@your-ec2-ip:/var/www/instagrowth/
```

## Setup Backend

```bash
cd /var/www/instagrowth/backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install emergent integrations (for OpenAI wrapper)
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
```

## Backend Requirements File

```bash
# /var/www/instagrowth/backend/requirements.txt should contain:
cat > requirements.txt << 'EOF'
fastapi==0.109.0
uvicorn[standard]==0.27.0
motor==3.3.2
pymongo==4.6.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
httpx==0.26.0
pydantic==2.5.3
python-dotenv==1.0.0
pyotp==2.9.0
qrcode==7.4.2
Pillow==10.2.0
aiohttp==3.9.1
resend==0.7.2
fpdf2==2.7.6
EOF
```

## Create Backend Environment File

```bash
cat > /var/www/instagrowth/backend/.env << 'EOF'
# MongoDB Configuration
MONGO_URL=mongodb://instagrowth_app:YOUR_APP_PASSWORD@localhost:27017/instagrowth_db?authSource=instagrowth_db
DB_NAME=instagrowth_db

# Security
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production-minimum-32-chars
ADMIN_SECRET_CODE=INSTAGROWTH_ADMIN_2024

# API Keys (Get from respective services)
OPENAI_API_KEY=your-openai-api-key
RESEND_API_KEY=your-resend-api-key
SENDER_EMAIL=noreply@yourdomain.com

# Stripe (Optional - for payments)
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key

# Meta/Instagram (Optional)
META_APP_ID=your-meta-app-id
META_APP_SECRET=your-meta-app-secret

# Frontend URL (for emails and redirects)
FRONTEND_URL=https://yourdomain.com
EOF
```

## Test Backend

```bash
cd /var/www/instagrowth/backend
source venv/bin/activate

# Test run
python -c "from server import app; print('Backend OK')"

# Start manually to test
uvicorn server:app --host 0.0.0.0 --port 8001

# Test API (in another terminal)
curl http://localhost:8001/api/
# Should return: {"message":"InstaGrowth OS API","version":"2.0.0"...}
```

---

# 7. FRONTEND DEPLOYMENT

## Setup Frontend

```bash
cd /var/www/instagrowth/frontend

# Install dependencies
yarn install

# Or with npm (not recommended)
# npm install
```

## Create Frontend Environment File

```bash
cat > /var/www/instagrowth/frontend/.env << 'EOF'
REACT_APP_BACKEND_URL=https://yourdomain.com
GENERATE_SOURCEMAP=false
EOF
```

## Build Frontend for Production

```bash
cd /var/www/instagrowth/frontend

# Build production bundle
yarn build

# This creates /var/www/instagrowth/frontend/build directory
```

---

# 8. NGINX CONFIGURATION

## Create Nginx Config

```bash
sudo nano /etc/nginx/sites-available/instagrowth
```

```nginx
# /etc/nginx/sites-available/instagrowth

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL certificates (will be added by Certbot)
    # ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml application/javascript application/json;
    gzip_disable "MSIE [1-6]\.";

    # Frontend - React App
    root /var/www/instagrowth/frontend/build;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API Proxy
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
        proxy_connect_timeout 75s;
        
        # CORS headers
        add_header 'Access-Control-Allow-Origin' '$http_origin' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
    }

    # Static files caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|pdf|txt|woff|woff2|ttf|svg)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Error pages
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```

## Enable Site

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/instagrowth /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

# 9. SSL CERTIFICATE (HTTPS)

## Get SSL with Certbot

```bash
# Make sure your domain DNS points to server IP first!

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow prompts:
# - Enter email
# - Agree to terms
# - Choose redirect (option 2)

# Test auto-renewal
sudo certbot renew --dry-run
```

## Auto-Renewal Cron

```bash
# Certbot automatically sets up renewal, verify with:
sudo systemctl status certbot.timer
```

---

# 10. ENVIRONMENT VARIABLES REFERENCE

## Backend (.env)

```bash
# Required Variables
MONGO_URL=mongodb://user:pass@localhost:27017/db_name?authSource=db_name
DB_NAME=instagrowth_db
JWT_SECRET=minimum-32-character-secret-key
ADMIN_SECRET_CODE=your-admin-code

# Email (Resend)
RESEND_API_KEY=re_xxxxxxxxxxxx
SENDER_EMAIL=noreply@yourdomain.com

# AI (Choose one)
OPENAI_API_KEY=sk-xxxx                    # Direct OpenAI
# OR use Emergent Key (already configured in code)

# Payments (Stripe)
STRIPE_SECRET_KEY=sk_live_xxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxx

# Instagram/Meta OAuth
META_APP_ID=your-app-id
META_APP_SECRET=your-app-secret
META_REDIRECT_URI=https://yourdomain.com/auth/instagram/callback

# Frontend URL
FRONTEND_URL=https://yourdomain.com
```

## Frontend (.env)

```bash
REACT_APP_BACKEND_URL=https://yourdomain.com
GENERATE_SOURCEMAP=false
```

---

# 11. PROCESS MANAGER (PM2)

## Install PM2

```bash
sudo npm install -g pm2
```

## Create PM2 Ecosystem File

```bash
cat > /var/www/instagrowth/ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'instagrowth-backend',
      cwd: '/var/www/instagrowth/backend',
      script: 'venv/bin/uvicorn',
      args: 'server:app --host 0.0.0.0 --port 8001 --workers 4',
      interpreter: 'none',
      env: {
        NODE_ENV: 'production',
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      error_file: '/var/log/pm2/instagrowth-backend-error.log',
      out_file: '/var/log/pm2/instagrowth-backend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    }
  ]
};
EOF
```

## Create Log Directory

```bash
sudo mkdir -p /var/log/pm2
sudo chown -R $USER:$USER /var/log/pm2
```

## Start Application with PM2

```bash
cd /var/www/instagrowth

# Start backend
pm2 start ecosystem.config.js

# Check status
pm2 status

# View logs
pm2 logs instagrowth-backend

# Save PM2 config
pm2 save

# Setup PM2 to start on boot
pm2 startup systemd
# Run the command it outputs (sudo env PATH=...)
```

## PM2 Commands Reference

```bash
# View all processes
pm2 list

# Restart app
pm2 restart instagrowth-backend

# Stop app
pm2 stop instagrowth-backend

# View logs
pm2 logs instagrowth-backend --lines 100

# Monitor
pm2 monit

# Reload (zero-downtime)
pm2 reload instagrowth-backend
```

---

# 12. DOMAIN CONFIGURATION

## DNS Settings (at your domain registrar)

```
Type    Name    Value               TTL
A       @       YOUR_EC2_PUBLIC_IP  300
A       www     YOUR_EC2_PUBLIC_IP  300
```

## Elastic IP (Recommended)

```bash
# AWS Console:
# 1. Go to EC2 > Elastic IPs
# 2. Allocate new address
# 3. Associate with your instance
# This gives you a static IP that doesn't change on reboot
```

---

# 13. MONITORING & LOGS

## View Logs

```bash
# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log

# PM2 app logs
pm2 logs instagrowth-backend

# System logs
sudo journalctl -u nginx -f
sudo journalctl -u mongod -f
```

## Setup Log Rotation

```bash
sudo nano /etc/logrotate.d/instagrowth
```

```
/var/log/pm2/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
    sharedscripts
    postrotate
        pm2 reloadLogs
    endscript
}
```

## Monitor Resources

```bash
# CPU and Memory
htop

# Disk usage
df -h

# MongoDB stats
mongosh --eval "db.serverStatus()"
```

---

# 14. TROUBLESHOOTING

## Common Issues

### Backend Not Starting

```bash
# Check logs
pm2 logs instagrowth-backend --lines 50

# Common fixes:
# 1. Missing packages
cd /var/www/instagrowth/backend
source venv/bin/activate
pip install -r requirements.txt

# 2. MongoDB connection
mongosh --eval "db.version()"

# 3. Port in use
sudo lsof -i :8001
```

### Frontend Not Loading

```bash
# Check Nginx config
sudo nginx -t

# Check if build exists
ls -la /var/www/instagrowth/frontend/build

# Rebuild if needed
cd /var/www/instagrowth/frontend
yarn build

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### MongoDB Connection Failed

```bash
# Check if running
sudo systemctl status mongod

# Start if stopped
sudo systemctl start mongod

# Check logs
sudo tail -f /var/log/mongodb/mongod.log

# Verify connection string
mongosh "mongodb://instagrowth_app:password@localhost:27017/instagrowth_db?authSource=instagrowth_db"
```

### SSL Certificate Issues

```bash
# Renew certificate
sudo certbot renew

# Check certificate status
sudo certbot certificates

# Force renewal
sudo certbot renew --force-renewal
```

### Permission Errors

```bash
# Fix ownership
sudo chown -R $USER:$USER /var/www/instagrowth

# Fix permissions
chmod -R 755 /var/www/instagrowth
```

---

# 15. QUICK DEPLOYMENT SCRIPT

Save this as `deploy.sh` for future updates:

```bash
#!/bin/bash

echo "🚀 Deploying InstaGrowth OS..."

# Navigate to app directory
cd /var/www/instagrowth

# Pull latest code
git pull origin main

# Backend update
echo "📦 Updating backend..."
cd /var/www/instagrowth/backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend update
echo "🎨 Building frontend..."
cd /var/www/instagrowth/frontend
yarn install
yarn build

# Restart services
echo "🔄 Restarting services..."
pm2 restart instagrowth-backend
sudo systemctl reload nginx

echo "✅ Deployment complete!"
```

```bash
# Make executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

---

# 16. PACKAGES SUMMARY

## Backend Python Packages

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
motor==3.3.2
pymongo==4.6.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
httpx==0.26.0
pydantic==2.5.3
python-dotenv==1.0.0
pyotp==2.9.0
qrcode==7.4.2
Pillow==10.2.0
aiohttp==3.9.1
resend==0.7.2
fpdf2==2.7.6

# Special package (Emergent Integrations)
emergentintegrations  # Install with: pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
```

## Frontend NPM Packages

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "framer-motion": "^10.16.0",
    "recharts": "^2.10.0",
    "lucide-react": "^0.303.0",
    "sonner": "^1.3.0",
    "tailwindcss": "^3.4.0",
    "@radix-ui/react-*": "various",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0"
  }
}
```

## System Packages

```bash
# Ubuntu packages
nodejs (20.x)
python3.11
python3.11-venv
python3-pip
nginx
mongodb-org (7.0)
certbot
python3-certbot-nginx
git
curl
wget
vim
htop
```

---

# 17. HEALTH CHECK ENDPOINTS

```bash
# Backend health
curl https://yourdomain.com/api/
# Expected: {"message":"InstaGrowth OS API","version":"2.0.0","docs":"/docs","status":"healthy"}

# Frontend
curl https://yourdomain.com/
# Expected: HTML content

# MongoDB (local only)
mongosh --eval "db.serverStatus().ok"
# Expected: 1
```

---

# 🎉 DEPLOYMENT COMPLETE!

Your InstaGrowth OS is now live at: https://yourdomain.com

## Default Admin Access:
- URL: https://yourdomain.com/admin-panel/login
- Email: superadmin@instagrowth.com
- Password: SuperAdmin123!
- Security Code: INSTAGROWTH_ADMIN_2024

## Next Steps:
1. Change default admin credentials
2. Configure Stripe for payments
3. Verify email domain in Resend
4. Submit Meta app for Instagram OAuth
5. Set up monitoring (optional: CloudWatch, Datadog)
6. Configure backups (MongoDB, files)

---

**Created: February 8, 2025**
**For: InstaGrowth OS v2.0.0**
