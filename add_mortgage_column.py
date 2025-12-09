import database

conn = database.get_db_connection()
c = conn.cursor()

try:
    # Check if column exists
    c.execute("SHOW COLUMNS FROM projects LIKE 'plots_to_mortgage'")
    if not c.fetchone():
        c.execute("ALTER TABLE projects ADD COLUMN plots_to_mortgage INT DEFAULT 0")
        conn.commit()
        print("Added plots_to_mortgage column successfully")
    else:
        print("Column plots_to_mortgage already exists")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
