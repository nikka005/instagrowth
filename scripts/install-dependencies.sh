#!/bin/bash

# ============================================
# InstaGrowth OS - Quick AWS Deployment Script
# Run this on a fresh Ubuntu 22.04 EC2 instance
# ============================================

echo "🚀 Starting InstaGrowth OS Deployment..."
echo "==========================================="

# Exit on error
set -e

# ============================================
# STEP 1: Update System
# ============================================
echo ""
echo "📦 Step 1: Updating system..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git vim htop unzip software-properties-common

# ============================================
# STEP 2: Install Node.js 20.x
# ============================================
echo ""
echo "📦 Step 2: Installing Node.js 20.x..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g yarn pm2
echo "Node version: $(node --version)"
echo "NPM version: $(npm --version)"

# ============================================
# STEP 3: Install Python 3.11
# ============================================
echo ""
echo "🐍 Step 3: Installing Python 3.11..."
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
echo "Python version: $(python3.11 --version)"

# ============================================
# STEP 4: Install MongoDB 7.0
# ============================================
echo ""
echo "🍃 Step 4: Installing MongoDB 7.0..."
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
   sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod
echo "MongoDB status: $(sudo systemctl is-active mongod)"

# ============================================
# STEP 5: Install Nginx
# ============================================
echo ""
echo "🌐 Step 5: Installing Nginx..."
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
echo "Nginx status: $(sudo systemctl is-active nginx)"

# ============================================
# STEP 6: Install Certbot
# ============================================
echo ""
echo "🔒 Step 6: Installing Certbot..."
sudo apt install -y certbot python3-certbot-nginx

# ============================================
# STEP 7: Create App Directory
# ============================================
echo ""
echo "📁 Step 7: Creating app directory..."
sudo mkdir -p /var/www/instagrowth
sudo chown -R $USER:$USER /var/www/instagrowth
sudo mkdir -p /var/log/pm2
sudo chown -R $USER:$USER /var/log/pm2

echo ""
echo "==========================================="
echo "✅ Base installation complete!"
echo "==========================================="
echo ""
echo "Next steps:"
echo "1. Upload your code to /var/www/instagrowth/"
echo "2. Run the setup-app.sh script"
echo ""
