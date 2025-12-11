
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def fix_permissions():
    print("Fixing permissions for Demolayouts Tenant...")
    try:
        # Connect to Demolayouts DB
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database="plotpro_demolayouts"
        )
        c = conn.cursor()
        
        # Update Admin User
        c.execute("UPDATE users SET can_view_dashboard = 1 WHERE role = 'admin'")
        conn.commit()
        
        # Verify
        c.execute("SELECT username, can_view_dashboard FROM users WHERE role = 'admin'")
        user = c.fetchone()
        
        conn.close()
        print(f"✅ Success! User '{user[0]}' dashboard permission set to: {user[1]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_permissions()
