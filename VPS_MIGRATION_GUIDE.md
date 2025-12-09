# 🚀 VPS Migration Guide - Ubuntu Deployment

## 📋 Overview

Your backup scripts will work on Ubuntu VPS with **minor adjustments**. This guide covers everything you need to migrate your application and backup system to an Ubuntu server.

---

## ✅ Compatibility Status

| Component | macOS | Ubuntu | Notes |
|-----------|-------|--------|-------|
| **Backup Script** | ✅ | ⚠️ Needs path adjustment | MySQL path different |
| **Restore Script** | ✅ | ⚠️ Needs path adjustment | MySQL path different |
| **GFS Retention** | ✅ | ✅ | Works identically |
| **Cron Jobs** | ✅ | ✅ | Same syntax |
| **Python App** | ✅ | ✅ | Fully compatible |
| **MySQL Database** | ✅ | ✅ | Fully compatible |

---

## 🔧 Required Adjustments for Ubuntu

### 1. MySQL Path Differences

**macOS:**
```bash
/usr/local/mysql-9.5.0-macos15-x86_64/bin/mysqldump
```

**Ubuntu (typical installations):**
```bash
/usr/bin/mysqldump  # Standard location
# OR
/usr/local/mysql/bin/mysqldump  # If installed from source
```

### 2. Backup Directory Path

**macOS:**
```bash
/Users/admin/receipt_backups
```

**Ubuntu (recommended):**
```bash
/var/backups/receipt_app
# OR
/home/username/backups/receipt_app
```

### 3. Project Directory Path

**macOS:**
```bash
/Users/admin/receipt_app_project_autogravity_ws
```

**Ubuntu (recommended):**
```bash
/var/www/receipt_app
# OR
/home/username/receipt_app
# OR
/opt/receipt_app
```

---

## 📦 Pre-Migration Checklist

### On Your Mac (Before Migration):

- [ ] Test all backups are working
- [ ] Export current database
- [ ] Document all environment variables
- [ ] List all Python dependencies
- [ ] Note MySQL version
- [ ] Backup all configuration files

### On Ubuntu VPS (Preparation):

- [ ] Update system packages
- [ ] Install MySQL/MariaDB
- [ ] Install Python 3.x
- [ ] Install required system packages
- [ ] Set up firewall
- [ ] Configure SSH access

---

## 🛠️ Ubuntu VPS Setup (Step-by-Step)

### Step 1: Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### Step 2: Install MySQL

```bash
# Install MySQL Server
sudo apt install mysql-server -y

# Secure MySQL installation
sudo mysql_secure_installation

# Start MySQL service
sudo systemctl start mysql
sudo systemctl enable mysql
```

### Step 3: Install Python & Dependencies

```bash
# Install Python 3 and pip
sudo apt install python3 python3-pip python3-venv -y

# Install system dependencies
sudo apt install build-essential libssl-dev libffi-dev python3-dev -y
sudo apt install libmysqlclient-dev -y
```

### Step 4: Install Additional Tools

```bash
# Install useful tools
sudo apt install git curl wget vim -y
sudo apt install nginx -y  # For production deployment
```

### Step 5: Create Application User (Optional but Recommended)

```bash
# Create dedicated user for the app
sudo useradd -m -s /bin/bash receiptapp
sudo passwd receiptapp

# Add to sudo group if needed
sudo usermod -aG sudo receiptapp
```

---

## 📁 Directory Structure on Ubuntu

### Recommended Production Structure:

```
/opt/receipt_app/                    # Application root
├── receipt_app.py                   # Main application
├── database.py                      # Database module
├── security_utils.py                # Security utilities
├── requirements.txt                 # Python dependencies
├── .env                             # Environment variables (secure!)
├── venv/                            # Python virtual environment
├── static/                          # Static files
├── templates/                       # HTML templates
├── backup_database.sh               # Backup script
├── restore_database.sh              # Restore script
└── logs/                            # Application logs

/var/backups/receipt_app/            # Backup storage
├── daily/                           # Daily backups
├── weekly/                          # Weekly backups
├── monthly/                         # Monthly backups
├── yearly/                          # Yearly backups
├── pre_restore/                     # Pre-restore backups
└── backup.log                       # Backup log

/var/log/receipt_app/                # Application logs
└── app.log                          # Main application log
```

---

## 🔄 Migration Process

### Phase 1: Transfer Files

#### Option A: Using SCP (Secure Copy)

```bash
# From your Mac, copy entire project to VPS
scp -r /Users/admin/receipt_app_project_autogravity_ws user@your-vps-ip:/opt/receipt_app

# Copy backup scripts separately
scp backup_database.sh restore_database.sh user@your-vps-ip:/opt/receipt_app/
```

#### Option B: Using Git (Recommended)

```bash
# On Mac: Push to Git repository
cd /Users/admin/receipt_app_project_autogravity_ws
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/receipt_app.git
git push -u origin main

# On Ubuntu: Clone repository
cd /opt
sudo git clone https://github.com/yourusername/receipt_app.git
sudo chown -R receiptapp:receiptapp receipt_app
```

#### Option C: Using rsync (Best for Large Files)

```bash
# From your Mac
rsync -avz -e ssh /Users/admin/receipt_app_project_autogravity_ws/ user@your-vps-ip:/opt/receipt_app/
```

### Phase 2: Database Migration

#### Export Database from Mac:

```bash
# On Mac
mysqldump -u root -p receipt_app > receipt_app_export.sql

# Compress for transfer
gzip receipt_app_export.sql

# Transfer to VPS
scp receipt_app_export.sql.gz user@your-vps-ip:/tmp/
```

#### Import Database on Ubuntu:

```bash
# On Ubuntu VPS
# Create database
mysql -u root -p -e "CREATE DATABASE receipt_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Create user
mysql -u root -p -e "CREATE USER 'receipt_user'@'localhost' IDENTIFIED BY 'strong_password_here';"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON receipt_app.* TO 'receipt_user'@'localhost';"
mysql -u root -p -e "FLUSH PRIVILEGES;"

# Import data
gunzip < /tmp/receipt_app_export.sql.gz | mysql -u root -p receipt_app

# Verify
mysql -u root -p receipt_app -e "SHOW TABLES;"
```

### Phase 3: Configure Application

#### Set Up Python Environment:

```bash
cd /opt/receipt_app

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Configure Environment Variables:

```bash
# Create .env file
nano /opt/receipt_app/.env
```

Add:
```env
# Database Configuration
DB_HOST=localhost
DB_USER=receipt_user
DB_PASSWORD=strong_password_here
DB_NAME=receipt_app

# Security Keys
SECRET_KEY=your_generated_secret_key_here
ENCRYPTION_KEY=your_generated_encryption_key_here

# Application Settings
FLASK_ENV=production
DEBUG=False
```

Secure the file:
```bash
chmod 600 /opt/receipt_app/.env
chown receiptapp:receiptapp /opt/receipt_app/.env
```

### Phase 4: Update Backup Scripts for Ubuntu

#### Update backup_database.sh:

```bash
nano /opt/receipt_app/backup_database.sh
```

Change these lines:
```bash
# OLD (macOS):
MYSQL_BIN="/usr/local/mysql-9.5.0-macos15-x86_64/bin"
BACKUP_ROOT="/Users/admin/receipt_backups"

# NEW (Ubuntu):
MYSQL_BIN="/usr/bin"  # Standard Ubuntu location
BACKUP_ROOT="/var/backups/receipt_app"
```

#### Update restore_database.sh:

```bash
nano /opt/receipt_app/restore_database.sh
```

Change:
```bash
# OLD (macOS):
MYSQL_BIN="/usr/local/mysql-9.5.0-macos15-x86_64/bin"
BACKUP_ROOT="/Users/admin/receipt_backups"

# NEW (Ubuntu):
MYSQL_BIN="/usr/bin"
BACKUP_ROOT="/var/backups/receipt_app"
```

#### Create Backup Directories:

```bash
sudo mkdir -p /var/backups/receipt_app/{daily,weekly,monthly,yearly,pre_restore}
sudo chown -R receiptapp:receiptapp /var/backups/receipt_app
sudo chmod 700 /var/backups/receipt_app
```

#### Make Scripts Executable:

```bash
chmod +x /opt/receipt_app/backup_database.sh
chmod +x /opt/receipt_app/restore_database.sh
```

### Phase 5: Test Backup System

```bash
# Test backup
cd /opt/receipt_app
./backup_database.sh

# Verify
ls -lh /var/backups/receipt_app/daily/
tail -20 /var/backups/receipt_app/backup.log
```

### Phase 6: Schedule Automated Backups

```bash
# Edit crontab for receiptapp user
sudo crontab -u receiptapp -e

# Add backup schedule (2 AM daily)
0 2 * * * /opt/receipt_app/backup_database.sh >> /var/backups/receipt_app/backup.log 2>&1

# Verify cron job
sudo crontab -u receiptapp -l
```

---

## 🔒 Production Security Hardening

### 1. Firewall Configuration

```bash
# Enable UFW firewall
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Check status
sudo ufw status
```

### 2. MySQL Security

```bash
# Bind MySQL to localhost only
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf

# Add/verify:
bind-address = 127.0.0.1

# Restart MySQL
sudo systemctl restart mysql
```

### 3. File Permissions

```bash
# Secure application files
sudo chown -R receiptapp:receiptapp /opt/receipt_app
sudo chmod 755 /opt/receipt_app
sudo chmod 600 /opt/receipt_app/.env
sudo chmod 600 /opt/receipt_app/database.py

# Secure backup directory
sudo chmod 700 /var/backups/receipt_app
```

### 4. Set Up HTTPS with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## 🚀 Production Deployment

### Option 1: Using Gunicorn (Recommended)

```bash
# Install Gunicorn
pip install gunicorn

# Create systemd service
sudo nano /etc/systemd/system/receipt_app.service
```

Add:
```ini
[Unit]
Description=Receipt Management Application
After=network.target mysql.service

[Service]
User=receiptapp
Group=receiptapp
WorkingDirectory=/opt/receipt_app
Environment="PATH=/opt/receipt_app/venv/bin"
ExecStart=/opt/receipt_app/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 receipt_app:app

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl start receipt_app
sudo systemctl enable receipt_app
sudo systemctl status receipt_app
```

### Option 2: Configure Nginx Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/receipt_app
```

Add:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/receipt_app/static;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/receipt_app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 📊 Monitoring & Maintenance

### Set Up Log Rotation

```bash
sudo nano /etc/logrotate.d/receipt_app
```

Add:
```
/var/backups/receipt_app/backup.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 receiptapp receiptapp
}

/var/log/receipt_app/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 receiptapp receiptapp
}
```

### Monitor Disk Space

```bash
# Check disk usage
df -h

# Check backup directory size
du -sh /var/backups/receipt_app
```

### Set Up Email Alerts (Optional)

```bash
# Install mailutils
sudo apt install mailutils -y

# Add to backup script for email notifications
echo "Backup completed" | mail -s "Backup Success" admin@yourdomain.com
```

---

## ✅ Post-Migration Checklist

- [ ] Application running on VPS
- [ ] Database migrated successfully
- [ ] All data verified
- [ ] Backup script working
- [ ] Restore script tested
- [ ] Cron jobs scheduled
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Nginx configured
- [ ] Application accessible via domain
- [ ] Email notifications working (if configured)
- [ ] Monitoring set up
- [ ] Documentation updated

---

## 🆘 Troubleshooting

### MySQL Connection Issues

```bash
# Check MySQL status
sudo systemctl status mysql

# Check MySQL error log
sudo tail -50 /var/log/mysql/error.log

# Test connection
mysql -u receipt_user -p -e "SELECT 1;"
```

### Backup Script Issues

```bash
# Check MySQL path
which mysqldump

# Test backup manually
/usr/bin/mysqldump -u receipt_user -p receipt_app > test.sql

# Check permissions
ls -la /var/backups/receipt_app
```

### Application Not Starting

```bash
# Check application logs
sudo journalctl -u receipt_app -n 50

# Check Python errors
cd /opt/receipt_app
source venv/bin/activate
python3 receipt_app.py
```

---

## 📚 Additional Resources

- **Ubuntu Server Guide:** https://ubuntu.com/server/docs
- **MySQL on Ubuntu:** https://dev.mysql.com/doc/mysql-apt-repo-quick-guide/en/
- **Nginx Documentation:** https://nginx.org/en/docs/
- **Gunicorn Documentation:** https://docs.gunicorn.org/
- **Let's Encrypt:** https://letsencrypt.org/getting-started/

---

## 💡 Pro Tips

1. **Test Everything Locally First** - Use a local Ubuntu VM before VPS
2. **Keep Mac Backups** - Don't delete Mac backups until VPS is stable
3. **Document Everything** - Keep notes of all changes made
4. **Use Git** - Version control makes rollbacks easy
5. **Monitor Logs** - Check logs regularly for issues
6. **Test Restores** - Monthly restore tests ensure backups work

---

## 🎯 Summary

**Your scripts WILL work on Ubuntu with these adjustments:**

✅ Change MySQL paths from macOS to Ubuntu locations
✅ Update backup directory paths
✅ Update project directory paths
✅ Everything else works identically!

**The migration is straightforward and well-documented!**
