import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("DB_HOST", "localhost")
user = os.getenv("DB_USER", "root")
password = os.getenv("DB_PASSWORD", "")

print(f"Connecting to MySQL at {host} as {user}...")
conn = mysql.connector.connect(host=host, user=user, password=password)
c = conn.cursor()

print("Creating 'receipt_app' database...")
try:
    c.execute("CREATE DATABASE IF NOT EXISTS receipt_app")
    print("✅ Database 'receipt_app' created successfully.")
except Exception as e:
    print(f"❌ Failed to create database: {e}")

conn.close()
