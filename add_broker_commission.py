import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "receipt_db")

def add_broker_commission_column():
    conn = None
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        print("Checking if 'broker_commission' column exists in 'commissions' table...")
        
        # Check if column exists
        cursor.execute("""
            SELECT count(*) 
            FROM information_schema.columns 
            WHERE table_schema = %s 
            AND table_name = 'commissions' 
            AND column_name = 'broker_commission'
        """, (DB_NAME,))
        
        if cursor.fetchone()[0] == 0:
            print("Adding 'broker_commission' column...")
            cursor.execute("ALTER TABLE commissions ADD COLUMN broker_commission DOUBLE DEFAULT 0.0")
            conn.commit()
            print("Column 'broker_commission' added successfully.")
        else:
            print("Column 'broker_commission' already exists.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    add_broker_commission_column()
