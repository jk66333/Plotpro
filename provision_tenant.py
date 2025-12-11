
import mysql.connector
import os
import secrets
import subprocess
from dotenv import load_dotenv

# Use Werkzeug for hashing provided default passwords
from werkzeug.security import generate_password_hash

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

def provision_new_tenant(name, subdomain, brand_color="#f16924", logo_url=None):
    """
    1. Create new DB `plotpro_<subdomain>`
    2. Import schema.sql
    3. Create Admin User
    4. Register in Master DB
    """
    tenant_db_name = f"plotpro_{subdomain}"
    print(f"--- Provisioning Tenant: {name} ({subdomain}) ---")

    # 1. Create Database
    conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
    c = conn.cursor()
    try:
        c.execute(f"CREATE DATABASE `{tenant_db_name}`")
        print(f"✅ Database {tenant_db_name} created.")
    except mysql.connector.Error as err:
        print(f"⚠️  Database creation failed (might exist): {err}")
    conn.close()

    
    # 2. Import Schema (Python-native)
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(base_dir, "schema.sql")
        
        with open(schema_path, 'r') as f:
            sql_script = f.read()
            
        # Execute script statement by statement
        t_conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=tenant_db_name)
        tc = t_conn.cursor()

        # Note: This is a basic split. For complex schemas with triggers or ; inside strings, 
        # a more robust parser is needed. For mysqldump outputs, this usually works.
        statements = sql_script.split(';')
        for statement in statements:
            stmt = statement.strip()
            if stmt:
                try:
                    tc.execute(stmt)
                except Exception as stmt_err:
                    # Ignore comment-only errors or empty commands
                    if not stmt.startswith("--") and not stmt.startswith("/*"):
                        print(f"⚠️ Warning executing statement: {stmt[:50]}... -> {stmt_err}")

        t_conn.commit()
        t_conn.close()
        print("✅ Schema imported successfully (Python-split).")
    except Exception as e:
        print(f"❌ Schema import failed: {e}")
        return False

    # 3. Create Default Admin User
    try:
        t_conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=tenant_db_name)
        tc = t_conn.cursor()
        
        # Default Admin Credentials
        admin_user = "admin"
        admin_pass = "password123"
        # Force a compatible method (PBKDF2) to avoid scrypt issues on some MacOS builds
        pass_hash = generate_password_hash(admin_pass, method='pbkdf2:sha256')
        
        tc.execute("INSERT INTO users (username, password_hash, role, created_at) VALUES (%s, %s, 'admin', NOW())", 
                   (admin_user, pass_hash))
        t_conn.commit()
        t_conn.close()
        print(f"✅ Admin user created (User: {admin_user}, Pass: {admin_pass})")
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")

    # 4. Register in Master DB
    try:
        m_conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database="plotpro_master")
        mc = m_conn.cursor()
        
        # Check if exists
        mc.execute("SELECT id FROM tenants WHERE subdomain=%s", (subdomain,))
        if mc.fetchone():
            print("⚠️  Tenant already exists in Master DB. Skipping insert.")
        else:
            mc.execute("""
                INSERT INTO tenants (name, subdomain, brand_color, logo_url, db_name, db_user, db_password, db_host)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, subdomain, brand_color, logo_url, tenant_db_name, DB_USER, DB_PASSWORD, DB_HOST))
            m_conn.commit()
            print("✅ Tenant registered in Master DB.")
        m_conn.close()
    except Exception as e:
        print(f"❌ Failed to register in Master DB: {e}")
        return False

    print(f"\n🎉 Tenant '{name}' is ready at http://{subdomain}.plotpro.in (mapped locally via HOSTS)")
    return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Provision a new SaaS Tenant')
    parser.add_argument('--name', help='Company Name', required=True)
    parser.add_argument('--subdomain', help='Subdomain (e.g. srinidhi)', required=True)
    parser.add_argument('--color', help='Brand Color (Hex)', default='#f16924')
    
    args = parser.parse_args()
    
    provision_new_tenant(args.name, args.subdomain, args.color)
