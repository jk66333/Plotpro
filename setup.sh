#!/bin/bash

echo "---------------------------------------------"
echo "  Receipt App — Automatic Setup for macOS"
echo "---------------------------------------------"

# Move to script directory
cd "$(dirname "$0")"

# Check for MySQL
if ! command -v mysql &> /dev/null; then
    echo "Error: MySQL is not installed. Please install it first:"
    echo "  brew install mysql"
    echo "  brew services start mysql"
    exit 1
fi

# 1. Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# 2. Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# 3. Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# 4. Install all required packages
echo "Installing Python dependencies..."
pip install -r requirements.txt

# 5. Install Playwright browser (Chromium)
echo "Installing Playwright Chromium..."
python -m playwright install chromium

# 6. Start the Receipt App
echo "Starting Receipt App..."
echo "Open your browser and go to:  http://localhost:5000"
python receipt_app.py
