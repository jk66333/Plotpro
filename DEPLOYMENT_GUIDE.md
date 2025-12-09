# Deployment Guide for Ubuntu 22.04 LTS

This guide provides step-by-step instructions to deploy the Receipt App on a fresh Ubuntu 22.04 Server.

## 1. System Setup & Prerequisites

First, update your system and install essential packages:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git mysql-server nginx curl
```

## 2. Database Setup (MySQL)

Secure your MySQL installation and create the database:

```bash
# Secure installation (follow prompts, set strong root password)
sudo mysql_secure_installation

# Log in to MySQL
sudo mysql -u root -p
```

Run the following SQL commands to create the database and user:

```sql
CREATE DATABASE receipt_app;
CREATE USER 'receipt_user'@'localhost' IDENTIFIED BY 'YOUR_STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON receipt_app.* TO 'receipt_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## 3. Application Setup

Clone your repository (replace URL with your repo):

```bash
cd /opt
sudo git clone https://github.com/JK66333/Plotpro.git receipt_app
sudo chown -R $USER:$USER receipt_app
cd receipt_app
```

Set up the Python Virtual Environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install Playwright browsers (required for PDF generation)
playwright install chromium
```

**Configuration (.env):**
Create a production `.env` file:

```bash
nano .env
```
Paste the following (update with your actual password and secret key):
```ini
DB_HOST=localhost
DB_USER=receipt_user
DB_PASSWORD=YOUR_STRONG_PASSWORD
DB_NAME=receipt_app
SECRET_KEY=CHANGE_THIS_TO_A_VERY_LONG_RANDOM_STRING
```

## 4. Gunicorn Setup (Application Server)

Test Gunicorn manually first to ensure it runs:
```bash
# While inside /opt/receipt_app
gunicorn -w 4 -b 0.0.0.0:8000 receipt_app:app
```
(Press Ctrl+C to stop after testing)

Create a Systemd service to keep the app running:

```bash
sudo nano /etc/systemd/system/receipt_app.service
```

Paste the following content:
```ini
[Unit]
Description=Gunicorn instance to serve Receipt App
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/opt/receipt_app
Environment="PATH=/opt/receipt_app/venv/bin"
ExecStart=/opt/receipt_app/venv/bin/gunicorn --workers 4 --bind unix:receipt_app.sock -m 007 receipt_app:app

[Install]
WantedBy=multi-user.target
```
*(Note: Change `User=ubuntu` to your actual VM username if different)*

Start and enable the service:
```bash
sudo systemctl start receipt_app
sudo systemctl enable receipt_app
```

## 5. Nginx Setup (Web Server)

Configure Nginx to proxy requests to Gunicorn:

```bash
sudo nano /etc/nginx/sites-available/receipt_app
```

Paste the following:
```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    location / {
        include proxy_params;
        proxy_pass http://unix:/opt/receipt_app/receipt_app.sock;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/receipt_app /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## 6. Security (Firewall)
Allow only SSH and HTTP/HTTPS traffic:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## 7. Migration & Admin Setup
Migration should happen automatically on first run via `init_db`. To create the first admin user, you may need to inspect the code or check logs, but the app creates a default `admin` with password `password123` if none exists. **Change this immediately after login.**

## Verification
Visit `http://YOUR_VM_IP` in your browser. You should see the login page.
