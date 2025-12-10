
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

def init_master_db():
    print("Connecting to MySQL Server...")
    # Connect without database first
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD
    )
    c = conn.cursor()

    print("Creating plotpro_master database...")
    c.execute("CREATE DATABASE IF NOT EXISTS plotpro_master")
    
    # Switch to master DB
    c.execute("USE plotpro_master")

    print("Creating tenants table...")
    c.execute("""
    CREATE TABLE IF NOT EXISTS tenants (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        subdomain VARCHAR(255) UNIQUE NOT NULL,
        brand_color VARCHAR(50) DEFAULT '#f16924',
        logo_url VARCHAR(500),
        
        -- Database Connection Details (The "Keys" to the Isolated DB)
        db_name VARCHAR(255) NOT NULL,
        db_user VARCHAR(255),
        db_password VARCHAR(255),
        db_host VARCHAR(255) DEFAULT 'localhost',
        
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Seed with a default/test tenant if table is empty
    c.execute("SELECT COUNT(*) FROM tenants")
    if c.fetchone()[0] == 0:
        print("Seeding default tenant 'localhost' pointing to 'receipt_app'...")
        # We assume the current "receipt_app" db is what we want to use for localhost dev
        c.execute("""
        INSERT INTO tenants (name, subdomain, db_name, db_user, db_password, db_host)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, ("Local Dev", "localhost", "receipt_app", DB_USER, DB_PASSWORD, DB_HOST))
        conn.commit()

    print("Master Database Initialized Successfully.")
    conn.close()

if __name__ == "__main__":
    init_master_db()
