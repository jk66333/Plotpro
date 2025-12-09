"""
Security utilities for the Receipt Management Application
Provides encryption, validation, and security helper functions
"""

import os
import re
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import session, request, abort, flash, redirect, url_for
from cryptography.fernet import Fernet
import hashlib


# ==================== Encryption ====================

class DataEncryption:
    """Handle encryption/decryption of sensitive data"""
    
    def __init__(self, key=None):
        """Initialize with encryption key from environment or generate new one"""
        if key is None:
            key = os.environ.get('ENCRYPTION_KEY')
        
        if key is None:
            # Generate a new key (for development only)
            key = Fernet.generate_key().decode()
            print(f"WARNING: Using generated encryption key. Set ENCRYPTION_KEY in .env")
            print(f"Generated key: {key}")
        
        if isinstance(key, str):
            key = key.encode()
            
        self.cipher = Fernet(key)
    
    def encrypt(self, data):
        """Encrypt string data"""
        if data is None or data == '':
            return None
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data):
        """Decrypt encrypted string data"""
        if encrypted_data is None or encrypted_data == '':
            return None
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            return None


# ==================== Input Validation ====================

class InputValidator:
    """Validate and sanitize user inputs"""
    
    @staticmethod
    def validate_pan(pan):
        """Validate PAN number format"""
        if not pan:
            return True, ""  # Optional field
        
        pan = pan.upper().strip()
        pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
        
        if not re.match(pattern, pan):
            return False, "Invalid PAN format. Should be: ABCDE1234F"
        return True, pan
    
    @staticmethod
    def validate_aadhar(aadhar):
        """Validate Aadhar number format"""
        if not aadhar:
            return True, ""  # Optional field
        
        # Remove spaces and validate
        aadhar_digits = aadhar.replace(' ', '').replace('-', '')
        
        if not aadhar_digits.isdigit() or len(aadhar_digits) != 12:
            return False, "Invalid Aadhar. Should be 12 digits"
        
        return True, aadhar_digits
    
    @staticmethod
    def validate_amount(amount):
        """Validate monetary amount"""
        try:
            # Remove commas and convert
            amount_str = str(amount).replace(',', '')
            amount_float = float(amount_str)
            
            if amount_float < 0:
                return False, "Amount cannot be negative"
            
            if amount_float > 999999999999:  # 1 trillion limit
                return False, "Amount too large"
            
            return True, amount_float
        except (ValueError, TypeError):
            return False, "Invalid amount format"
    
    @staticmethod
    def sanitize_string(text, max_length=255):
        """Sanitize string input"""
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        text = str(text).strip()
        
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        # Truncate to max length
        return text[:max_length]
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email:
            return True, ""
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"
        
        return True, email.lower()
    
    @staticmethod
    def validate_phone(phone):
        """Validate Indian phone number"""
        if not phone:
            return True, ""
        
        # Remove spaces, dashes, parentheses
        phone_digits = re.sub(r'[\s\-\(\)\+]', '', phone)
        
        # Check for 10 digits (Indian mobile) or 11-13 (with country code)
        if not phone_digits.isdigit():
            return False, "Phone number should contain only digits"
        
        if len(phone_digits) not in [10, 11, 12, 13]:
            return False, "Invalid phone number length"
        
        return True, phone_digits


# ==================== Password Security ====================

class PasswordPolicy:
    """Enforce password security policies"""
    
    MIN_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    
    @classmethod
    def validate(cls, password):
        """Validate password against security policy"""
        errors = []
        
        if len(password) < cls.MIN_LENGTH:
            errors.append(f"Password must be at least {cls.MIN_LENGTH} characters long")
        
        if cls.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if cls.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if cls.REQUIRE_DIGIT and not re.search(r'[0-9]', password):
            errors.append("Password must contain at least one digit")
        
        if cls.REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        # Check for common passwords
        common_passwords = ['password', '12345678', 'qwerty', 'admin', 'letmein']
        if password.lower() in common_passwords:
            errors.append("Password is too common. Please choose a stronger password")
        
        if errors:
            return False, errors
        
        return True, ["Password meets security requirements"]
    
    @staticmethod
    def generate_secure_password(length=16):
        """Generate a cryptographically secure random password"""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
        return ''.join(secrets.choice(alphabet) for _ in range(length))


# ==================== Session Security ====================

def require_login(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def require_admin(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login', next=request.url))
        
        if session.get('role') != 'admin':
            flash('You do not have permission to access this page', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


# ==================== Audit Logging ====================

class AuditLogger:
    """Log security-relevant events"""
    
    @staticmethod
    def log_event(user_id, action, resource, details=None, severity='INFO'):
        """
        Log an audit event
        
        Args:
            user_id: ID of user performing action
            action: Action performed (LOGIN, LOGOUT, CREATE, UPDATE, DELETE, VIEW)
            resource: Resource affected (RECEIPT, USER, COMMISSION, etc.)
            details: Additional details (dict or string)
            severity: INFO, WARNING, ERROR, CRITICAL
        """
        try:
            import database
            conn = database.get_db_connection()
            c = conn.cursor()
            
            # Create audit_logs table if it doesn't exist
            c.execute("""
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
                )
            """)
            
            # Get username from session
            username = session.get('username', 'anonymous')
            
            # Get IP address
            ip_address = request.remote_addr if request else 'system'
            
            # Get user agent
            user_agent = request.headers.get('User-Agent', '') if request else ''
            
            # Convert details to JSON string if dict
            if isinstance(details, dict):
                import json
                details = json.dumps(details)
            
            # Insert audit log
            c.execute("""
                INSERT INTO audit_logs 
                (user_id, username, action, resource, details, severity, ip_address, user_agent)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, username, action, resource, details, severity, ip_address, user_agent))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Audit logging error: {e}")
            # Don't fail the main operation if logging fails


# ==================== Rate Limiting ====================

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.attempts = {}  # {ip: [(timestamp, action), ...]}
    
    def check_rate_limit(self, identifier, max_attempts=5, window_minutes=15):
        """
        Check if rate limit is exceeded
        
        Args:
            identifier: IP address or user ID
            max_attempts: Maximum attempts allowed
            window_minutes: Time window in minutes
        
        Returns:
            (allowed: bool, remaining_attempts: int, reset_time: datetime)
        """
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        
        # Clean old attempts
        if identifier in self.attempts:
            self.attempts[identifier] = [
                (ts, action) for ts, action in self.attempts[identifier]
                if ts > window_start
            ]
        else:
            self.attempts[identifier] = []
        
        # Check current attempts
        current_attempts = len(self.attempts[identifier])
        
        if current_attempts >= max_attempts:
            # Calculate when the oldest attempt will expire
            oldest_attempt = min(ts for ts, _ in self.attempts[identifier])
            reset_time = oldest_attempt + timedelta(minutes=window_minutes)
            return False, 0, reset_time
        
        # Record this attempt
        self.attempts[identifier].append((now, 'attempt'))
        
        remaining = max_attempts - current_attempts - 1
        reset_time = now + timedelta(minutes=window_minutes)
        
        return True, remaining, reset_time
    
    def reset(self, identifier):
        """Reset rate limit for identifier"""
        if identifier in self.attempts:
            del self.attempts[identifier]


# Global rate limiter instance
login_rate_limiter = RateLimiter()


# ==================== Security Headers ====================

def add_security_headers(response):
    """Add security headers to response"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Content Security Policy
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net fonts.googleapis.com; "
        "font-src 'self' fonts.gstatic.com cdn.jsdelivr.net; "
        "img-src 'self' data:; "
        "connect-src 'self'"
    )
    response.headers['Content-Security-Policy'] = csp
    
    return response


# ==================== Utility Functions ====================

def generate_secure_token(length=32):
    """Generate a cryptographically secure random token"""
    return secrets.token_urlsafe(length)


def hash_file(filepath):
    """Generate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def is_safe_redirect_url(target):
    """Check if redirect URL is safe (same domain)"""
    if not target:
        return False
    
    from urllib.parse import urlparse, urljoin
    from flask import request
    
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


# ==================== Export ====================

__all__ = [
    'DataEncryption',
    'InputValidator',
    'PasswordPolicy',
    'AuditLogger',
    'RateLimiter',
    'login_rate_limiter',
    'require_login',
    'require_admin',
    'add_security_headers',
    'generate_secure_token',
    'hash_file',
    'is_safe_redirect_url',
]
