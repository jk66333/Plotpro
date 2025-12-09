import sqlite3
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

SQLITE_DB = "receipts.db"
MYSQL_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "receipt_app")
}

def migrate():
    print("Starting migration...")
    
    if not os.path.exists(SQLITE_DB):
        print(f"SQLite database {SQLITE_DB} not found.")
        return

    # Connect to SQLite
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    # Connect to MySQL
    try:
        # Connect to server first to create DB
        mysql_conn = mysql.connector.connect(
            host=MYSQL_CONFIG["host"],
            user=MYSQL_CONFIG["user"],
            password=MYSQL_CONFIG["password"]
        )
        mysql_cur = mysql_conn.cursor()
        
        # Create Database
        mysql_cur.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
        mysql_cur.execute(f"USE {MYSQL_CONFIG['database']}")
        print(f"Connected to MySQL database: {MYSQL_CONFIG['database']}")
        
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        print("Please check your .env file or DB credentials.")
        return

    # Drop existing tables to ensure clean state
    tables = ["pending_receipts", "users", "commissions", "projects", "receipts"]
    for table in tables:
        mysql_cur.execute(f"DROP TABLE IF EXISTS {table}")

    # Create Tables
    print("Creating tables...")
    
    # Receipts Table
    mysql_cur.execute("""
    CREATE TABLE receipts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        no VARCHAR(255),
        project_name VARCHAR(255),
        date VARCHAR(255),
        venture VARCHAR(255),
        customer_name VARCHAR(255),
        amount_numeric DOUBLE,
        amount_words TEXT,
        plot_no VARCHAR(255),
        square_yards VARCHAR(255),
        purpose TEXT,
        drawn_bank VARCHAR(255),
        branch VARCHAR(255),
        payment_mode VARCHAR(255),
        created_at VARCHAR(255),
        pan_no VARCHAR(255),
        aadhar_no VARCHAR(255),
        instrument_no VARCHAR(255),
        basic_price VARCHAR(255)
    )
    """)

    # Projects Table
    mysql_cur.execute("""
    CREATE TABLE projects (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) UNIQUE,
        total_plots INT DEFAULT 0,
        plots_to_landowners INT DEFAULT 0
    )
    """)

    # Commissions Table
    mysql_cur.execute("""
    CREATE TABLE commissions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        plot_no VARCHAR(255),
        sq_yards DOUBLE,
        original_price DOUBLE,
        negotiated_price DOUBLE,
        advance_received DOUBLE,
        agent_commission_rate DOUBLE,
        agreement_percentage DOUBLE,
        amount_paid_at_agreement DOUBLE,
        amc_charges DOUBLE,
        cgm_rate DOUBLE,
        srgm_rate DOUBLE,
        gm_rate DOUBLE,
        agent_rate DOUBLE,
        total_amount DOUBLE,
        w_value DOUBLE,
        b_value DOUBLE,
        balance_amount DOUBLE,
        actual_agreement_amount DOUBLE,
        agreement_balance DOUBLE,
        mediator_amount DOUBLE,
        mediator_deduction DOUBLE,
        mediator_actual_payment DOUBLE,
        mediator_at_agreement DOUBLE,
        cgm_total DOUBLE,
        cgm_at_agreement DOUBLE,
        cgm_at_registration DOUBLE,
        srgm_total DOUBLE,
        srgm_at_agreement DOUBLE,
        srgm_at_registration DOUBLE,
        gm_total DOUBLE,
        gm_at_agreement DOUBLE,
        gm_at_registration DOUBLE,
        agent_total DOUBLE,
        agent_at_agreement DOUBLE,
        agent_at_registration DOUBLE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by VARCHAR(255),
        cgm_name VARCHAR(255),
        srgm_name VARCHAR(255),
        gm_name VARCHAR(255),
        agent_name VARCHAR(255),
        project_name VARCHAR(255),
        commission_breakdown TEXT
    )
    """)

    # Users Table
    mysql_cur.execute("""
    CREATE TABLE users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(50) NOT NULL DEFAULT 'user',
        can_view_dashboard TINYINT(1) NOT NULL DEFAULT 0,
        created_at VARCHAR(255) NOT NULL,
        can_search_receipts TINYINT(1) NOT NULL DEFAULT 0,
        can_view_vishvam_layout TINYINT(1) NOT NULL DEFAULT 0
    )
    """)

    # Pending Receipts Table
    mysql_cur.execute("""
    CREATE TABLE pending_receipts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        no VARCHAR(255),
        project_name VARCHAR(255),
        date VARCHAR(255),
        venture VARCHAR(255),
        customer_name VARCHAR(255),
        amount_numeric DOUBLE,
        amount_words TEXT,
        plot_no VARCHAR(255),
        square_yards VARCHAR(255),
        purpose TEXT,
        drawn_bank VARCHAR(255),
        branch VARCHAR(255),
        payment_mode VARCHAR(255),
        instrument_no VARCHAR(255),
        submitted_by VARCHAR(255),
        submitted_at VARCHAR(255),
        status VARCHAR(50) DEFAULT 'pending',
        admin_notes TEXT
    )
    """)

    # Migrate Data
    tables_to_migrate = ["receipts", "projects", "commissions", "users", "pending_receipts"]
    
    for table in tables_to_migrate:
        print(f"Migrating data for {table}...")
        try:
            sqlite_cur.execute(f"SELECT * FROM {table}")
            rows = sqlite_cur.fetchall()
            
            if not rows:
                print(f"No data in {table}")
                continue
            
            # Get column names from SQLite cursor
            columns = [description[0] for description in sqlite_cur.description]
            
            # Filter columns that exist in MySQL table (in case of mismatch)
            # For simplicity, assuming columns match or are subset. 
            # Ideally we should check MySQL columns too.
            
            placeholders = ", ".join(["%s"] * len(columns))
            col_names = ", ".join(columns)
            
            sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
            
            data = [tuple(row) for row in rows]
            
            # Batch insert
            batch_size = 1000
            for i in range(0, len(data), batch_size):
                batch = data[i:i+batch_size]
                mysql_cur.executemany(sql, batch)
            
            print(f"Migrated {len(data)} rows to {table}")
            
        except Exception as e:
            print(f"Error migrating {table}: {e}")

    mysql_conn.commit()
    sqlite_conn.close()
    mysql_conn.close()
    print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
