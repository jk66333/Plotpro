import database

DB_PATH = "receipts.db"

def init_db():
    conn = database.get_db_connection()
    c = conn.cursor()
    
    # Create projects table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE
        );
        """
    )
    
    # Insert default projects if they don't exist
    default_projects = ["Vishvam", "Srinidhi", "Prakruthi"]
    for p in default_projects:
        try:
            c.execute("INSERT INTO projects (name) VALUES (%s)", (p,))
            print(f"Inserted {p}")
        except database.IntegrityError:
            print(f"Skipped {p} (already exists)")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
