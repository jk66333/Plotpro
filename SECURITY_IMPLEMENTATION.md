# Quick Security Implementation Guide

## Step 1: Install Required Dependencies

```bash
pip install cryptography flask-limiter python-dotenv
```

Add to `requirements.txt`:
```
cryptography>=41.0.0
flask-limiter>=3.5.0
python-dotenv>=1.0.0
```

## Step 2: Generate Secure Keys

Run these commands to generate secure keys:

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

# Generate ENCRYPTION_KEY
python3 -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
```

## Step 3: Update .env File

Add the generated keys to your `.env` file:

```env
SECRET_KEY=<your_generated_secret_key>
ENCRYPTION_KEY=<your_generated_encryption_key>
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=<your_strong_password>
DB_NAME=receipt_app
```

## Step 4: Secure the .env File

```bash
# Set restrictive permissions
chmod 600 .env

# Add to .gitignore if not already there
echo ".env" >> .gitignore
```

## Step 5: Update receipt_app.py

### 5.1: Update Secret Key (Line 40)

**Before:**
```python
app.secret_key = "CHANGE_THIS_SECRET_KEY_123456789"
```

**After:**
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24)
```

### 5.2: Add Security Configurations

Add after `app.secret_key`:

```python
from datetime import timedelta

# Session security
app.config.update(
    SESSION_COOKIE_SECURE=False,  # Set to True when using HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(hours=2)
)
```

### 5.3: Import Security Utils

Add at the top of receipt_app.py:

```python
from security_utils import (
    AuditLogger,
    InputValidator,
    PasswordPolicy,
    login_rate_limiter,
    add_security_headers,
    require_login,
    require_admin
)
```

### 5.4: Add Security Headers

Add this after creating the app:

```python
@app.after_request
def apply_security_headers(response):
    return add_security_headers(response)
```

### 5.5: Add Rate Limiting to Login

Update the login route:

```python
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Get IP address
        ip_address = request.remote_addr
        
        # Check rate limit
        allowed, remaining, reset_time = login_rate_limiter.check_rate_limit(
            ip_address, 
            max_attempts=5, 
            window_minutes=15
        )
        
        if not allowed:
            flash(f'Too many login attempts. Please try again after {reset_time.strftime("%H:%M")}', 'danger')
            return render_template("login.html")
        
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        # ... rest of login code ...
        
        # On successful login, reset rate limit
        if valid:
            login_rate_limiter.reset(ip_address)
            # ... rest of success code ...
```

### 5.6: Add Audit Logging

Add audit logging to critical operations:

```python
# After successful login
AuditLogger.log_event(
    user_id=user_id,
    action='LOGIN',
    resource='AUTH',
    details=f'User {username} logged in successfully'
)

# After creating a receipt
AuditLogger.log_event(
    user_id=session.get('user_id'),
    action='CREATE',
    resource='RECEIPT',
    details=f'Created receipt #{receipt_no} for plot {plot_no}'
)

# After deleting data
AuditLogger.log_event(
    user_id=session.get('user_id'),
    action='DELETE',
    resource='RECEIPT',
    details=f'Deleted receipt #{receipt_id}',
    severity='WARNING'
)
```

### 5.7: Add Input Validation

For receipt creation/editing:

```python
# Validate PAN
valid, pan_value = InputValidator.validate_pan(pan_no)
if not valid:
    flash(pan_value, 'danger')
    return redirect(url_for('index'))

# Validate Aadhar
valid, aadhar_value = InputValidator.validate_aadhar(aadhar_no)
if not valid:
    flash(aadhar_value, 'danger')
    return redirect(url_for('index'))

# Validate Amount
valid, amount_value = InputValidator.validate_amount(amount_numeric)
if not valid:
    flash(amount_value, 'danger')
    return redirect(url_for('index'))
```

### 5.8: Disable Debug Mode in Production

At the bottom of receipt_app.py:

```python
if __name__ == "__main__":
    init_db()
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(os.path.join("static", "css"), exist_ok=True)
    
    # Only enable debug in development
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, port=5000)
```

## Step 6: Database Security

### 6.1: Create Audit Logs Table

Run this SQL:

```sql
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    username VARCHAR(255),
    action VARCHAR(50),
    resource VARCHAR(50),
    details TEXT,
    severity VARCHAR(20),
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_timestamp (timestamp)
);
```

### 6.2: Set Up Database Backups

Create a backup script `backup_database.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$HOME/receipt_backups"
DB_NAME="receipt_app"
DB_USER="root"
DB_PASS="your_password"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Backup database
mysqldump -u $DB_USER -p$DB_PASS $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: backup_$DATE.sql.gz"
```

Make it executable:
```bash
chmod +x backup_database.sh
```

Set up daily cron job:
```bash
crontab -e
# Add this line:
0 2 * * * /path/to/backup_database.sh
```

## Step 7: Password Policy Enforcement

Update user creation to enforce password policy:

```python
@app.route("/user_management", methods=["POST"])
@require_admin
def user_management_post():
    action = request.form.get("action")
    
    if action == "create":
        password = request.form.get("password")
        
        # Validate password strength
        valid, messages = PasswordPolicy.validate(password)
        if not valid:
            for msg in messages:
                flash(msg, 'danger')
            return redirect(url_for('user_management'))
        
        # ... rest of user creation code ...
```

## Step 8: Testing

### 8.1: Test Rate Limiting

Try logging in with wrong password 6 times - should be blocked.

### 8.2: Test Audit Logging

Check audit_logs table after various operations:

```sql
SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 10;
```

### 8.3: Test Input Validation

Try entering invalid PAN/Aadhar - should show error messages.

## Step 9: Monitoring

### View Recent Audit Logs

```sql
SELECT 
    username, 
    action, 
    resource, 
    details, 
    timestamp 
FROM audit_logs 
WHERE timestamp > DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY timestamp DESC;
```

### Check Failed Login Attempts

```sql
SELECT 
    ip_address, 
    COUNT(*) as attempts,
    MAX(timestamp) as last_attempt
FROM audit_logs 
WHERE action = 'LOGIN_FAILED'
  AND timestamp > DATE_SUB(NOW(), INTERVAL 1 HOUR)
GROUP BY ip_address
HAVING attempts > 3;
```

## Step 10: Production Deployment

### Use Production WSGI Server

Install gunicorn:
```bash
pip install gunicorn
```

Run with:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 receipt_app:app
```

### Set Up HTTPS with Nginx

Example nginx configuration:

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## Quick Checklist

- [ ] Install dependencies
- [ ] Generate and set SECRET_KEY
- [ ] Generate and set ENCRYPTION_KEY
- [ ] Secure .env file (chmod 600)
- [ ] Add .env to .gitignore
- [ ] Update app.secret_key in receipt_app.py
- [ ] Add security headers
- [ ] Implement rate limiting on login
- [ ] Add audit logging to critical operations
- [ ] Create audit_logs table
- [ ] Set up database backups
- [ ] Enforce password policy
- [ ] Disable debug mode in production
- [ ] Test all security features
- [ ] Set up HTTPS for production
- [ ] Monitor audit logs regularly

## Need Help?

Refer to:
- `SECURITY_GUIDE.md` for detailed explanations
- `security_utils.py` for available security functions
- `.env.example` for configuration template
