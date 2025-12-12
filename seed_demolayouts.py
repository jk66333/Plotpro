
import mysql.connector
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
import datetime
import random

load_dotenv()

def seed_data():
    print("Seeding Demolayouts Data...")
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database="plotpro_demolayouts"
        )
        c = conn.cursor()
        
        # 1. Clear existing data
        c.execute("DELETE FROM receipts")
        c.execute("DELETE FROM projects")
        
        # 2. Insert Projects
        projects = [
            ("Sunflower Gardens", 150, 20),
            ("Green Valley", 60, 5),
            ("Harmony Heights", 40, 0)
        ]
        c.executemany("INSERT INTO projects (name, total_plots, plots_to_landowners) VALUES (%s, %s, %s)", projects)
        print(f"✅ Added {len(projects)} Projects")
        
        # 3. Create Receipts (Simulate Sold Plots)
        receipts = []
        payment_modes = ["CASH", "Online Transfer", "Cheque"]
        
        for i in range(1, 46): # Increased to 45 receipts for better data density
            basic_price = random.randint(15000, 25000)
            sq_yards = random.randint(180, 250)
            payment_mode = random.choice(payment_modes)
            
            receipts.append((
                f"REC-{i:03d}",
                f"Customer {i}",
                "Sunflower Gardens" if i <= 25 else "Green Valley",
                f"{i}", # Plot No
                120000,
                datetime.date.today() - datetime.timedelta(days=i),
                str(basic_price), # basic_price is varchar in schema
                str(sq_yards),    # square_yards is varchar in schema
                payment_mode
            ))
            
        c.executemany("""
            INSERT INTO receipts (no, customer_name, project_name, plot_no, amount_numeric, date, basic_price, square_yards, payment_mode) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, receipts)
        print(f"✅ Added {len(receipts)} Receipts with random Price/Area/Payment data")
        
        conn.commit()
        conn.close()
        print("✅ Seeding Complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    seed_data()
