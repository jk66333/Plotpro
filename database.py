import mysql.connector
import os
from dotenv import load_dotenv
from mysql.connector import Error, IntegrityError, OperationalError

load_dotenv()

# Export these for use in receipt_app.py
__all__ = ['get_db_connection', 'fetch_one', 'fetch_all', 'IntegrityError', 'OperationalError', 'Error']


def get_db_connection():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "receipt_app")
    )
    return conn

class MySQLRow(dict):
    """
    A wrapper to provide dictionary-like access to rows.
    """
    def __init__(self, cursor, row):
        self._row = row
        self._columns = [col[0] for col in cursor.description]
        # Initialize dict with column names mapping to values
        super().__init__(zip(self._columns, row))
        
    def __getitem__(self, key):
        if isinstance(key, int):
            return self._row[key]
        return super().__getitem__(key)

def get_cursor(conn):
    """Returns a cursor that yields MySQLRow objects"""
    cursor = conn.cursor()
    # Return the standard cursor
    return cursor
    return cursor

# Helper to fetch one row as MySQLRow
def fetch_one(cursor):
    row = cursor.fetchone()
    if row is None:
        return None
    return MySQLRow(cursor, row)

# Helper to fetch all rows as MySQLRows
def fetch_all(cursor):
    rows = cursor.fetchall()
    if not rows:
        return []
    return [MySQLRow(cursor, row) for row in rows]
