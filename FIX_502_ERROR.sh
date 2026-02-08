#!/bin/bash
# ================================================================
# FIX: Backend Not Running (502 Bad Gateway)
# Run these commands on your AWS server via SSH
# ================================================================

# 1. First, check PM2 status
pm2 status

# 2. If backend is not running, check the logs
pm2 logs instagrowth-backend --lines 50

# 3. If no processes exist, start fresh:
cd /var/www/instagrowth

# 4. Make sure virtual environment is set up
cd /var/www/instagrowth/backend
source venv/bin/activate

# 5. Install any missing packages
pip install -r requirements.txt
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/

# 6. Test if server can start manually
python -c "from server import app; print('Server OK')"

# 7. Start with PM2
cd /var/www/instagrowth
pm2 start ecosystem.config.js

# 8. Save PM2 config so it survives reboot
pm2 save

# 9. Check if it's running now
pm2 status

# 10. Test the API
curl http://localhost:8001/api/

# ================================================================
# COMMON ISSUES & FIXES
# ================================================================

# Issue: Module not found errors
# Fix: Install missing packages
cd /var/www/instagrowth/backend
source venv/bin/activate
pip install -r requirements.txt

# Issue: MongoDB not running
# Fix: Start MongoDB
sudo systemctl start mongod
sudo systemctl status mongod

# Issue: Wrong Python version
# Fix: Make sure using Python 3.11
python3.11 -m venv venv
source venv/bin/activate

# Issue: Permission denied
# Fix: Change ownership
sudo chown -R $USER:$USER /var/www/instagrowth

# ================================================================
# QUICK DEBUG COMMANDS
# ================================================================

# Check what's running on port 8001
sudo lsof -i :8001

# Check PM2 logs in real-time
pm2 logs instagrowth-backend

# Restart everything
pm2 restart instagrowth-backend
sudo systemctl reload nginx

# Kill and restart PM2
pm2 kill
cd /var/www/instagrowth
pm2 start ecosystem.config.js
pm2 save
