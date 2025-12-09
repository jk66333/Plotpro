# MySQL Migration Guide

This project has been migrated from SQLite to MySQL. Follow these steps to complete the setup.

## 1. Install MySQL Server
Ensure you have MySQL Server installed and running on your machine.
- **Mac**: `brew install mysql` then `brew services start mysql`
- **Windows**: Download installer from MySQL website
- **Linux**: `sudo apt install mysql-server`

## 2. Configure Credentials
Edit the `.env` file in the project root with your MySQL credentials:
```ini
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password  # Leave empty if no password
DB_NAME=receipt_app
```

## 3. Install Dependencies
Install the required Python packages:
```bash
venv/bin/pip install -r requirements.txt
```

## 4. Run Migration Script
This script will create the MySQL database and tables, and copy all data from the existing `receipts.db` SQLite database.
```bash
venv/bin/python migrate_to_mysql.py
```

## 5. Run the Application
Start the application as usual:
```bash
venv/bin/python receipt_app.py
```
