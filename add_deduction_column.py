import database
import mysql.connector

def add_column():
    conn = database.get_db_connection()
    c = conn.cursor()
    
    try:
        print("Attempting to add mediator_deduction column...")
        c.execute("ALTER TABLE commissions ADD COLUMN mediator_deduction DOUBLE DEFAULT 0.0")
        conn.commit()
        print("Successfully added mediator_deduction column.")
    except mysql.connector.Error as err:
        if "Duplicate column name" in str(err):
            print("Column mediator_deduction already exists.")
        else:
            print(f"Error adding column: {err}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_column()
