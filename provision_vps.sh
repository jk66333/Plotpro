#!/bin/bash

# PlotPro SaaS - VPS Provisioning Script
# Support: Ubuntu 22.04 LTS
# Run as root: sudo ./provision_vps.sh

echo "--- 🚀 Starting VPS Provisioning for PlotPro ---"

# 1. Update System
echo "--- 📦 Updating System Packages ---"
apt-get update && apt-get upgrade -y

# 2. Install Dependencies
echo "--- 🛠 Installing Python, MySQL, Nginx, Certbot ---"
apt-get install -y python3-pip python3-dev python3-venv \
    libmysqlclient-dev build-essential \
    mysql-server \
    nginx \
    certbot python3-certbot-nginx \
    git \
    supervisor

# 3. Install Playwright Dependencies (Browsers)
echo "--- 🎭 Installing Playwright System Deps ---"
# This is needed for PDF generation to work on Linux
pip3 install playwright
playwright install --with-deps chromium

# 4. Secure MySQL
echo "--- 🔒 Securing MySQL ---"
# Note: You will need to manually run 'mysql_secure_installation' if you want strict security,
# or we can set a root password here. For automation, we'll strict creation locally.
# We will create the plotpro_master database.

service mysql start

echo "--- ✅ Provisioning Complete! ---"
echo "Next Steps:"
echo "1. Clone your code to /var/www/plotpro"
echo "2. Create a .env file with your DB credentials"
echo "3. Run 'python3 init_saas_master.py'"
echo "4. Configure Nginx"
