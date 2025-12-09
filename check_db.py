import sqlite3
import os

DB_PATH = "receipts.db"

if not os.path.exists(DB_PATH):
    print(f"Database not found at {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("Checking commissions table for plot 490...")
c.execute("SELECT id, plot_no, project_name FROM commissions WHERE plot_no = '490'")
rows = c.fetchall()

if not rows:
    print("No records found for plot 490.")
else:
    print(f"Found {len(rows)} records:")
    for row in rows:
        print(f"ID: {row['id']}, Plot: {row['plot_no']}, Project: '{row['project_name']}'")

conn.close()
