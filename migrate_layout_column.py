import database
import mysql.connector

def migrate():
    print("--- Starting Migration: Add layout_svg_path to projects table ---")
    try:
        conn = database.get_db_connection()
        c = conn.cursor()
        
        # Check if column exists
        c.execute("SHOW COLUMNS FROM projects LIKE 'layout_svg_path'")
        if c.fetchone():
            print("Column 'layout_svg_path' already exists. No action needed.")
        else:
            print("Column not found. Adding 'layout_svg_path'...")
            c.execute("ALTER TABLE projects ADD COLUMN layout_svg_path VARCHAR(255) DEFAULT NULL")
            print("Successfully added column 'layout_svg_path'.")
            
        conn.commit()
        conn.close()
        print("--- Migration Complete ---\n")
        
    except Exception as e:
        print(f"Migration Failed: {e}")

if __name__ == "__main__":
    migrate()
