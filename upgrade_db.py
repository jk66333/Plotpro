import sqlite3

conn = sqlite3.connect("receipts.db")
c = conn.cursor()

try:
    c.execute("ALTER TABLE receipts ADD COLUMN instrument_no TEXT;")
    print("Column added successfully.")
except Exception as e:
    print("Already exists or error:", e)

conn.commit()
conn.close()
