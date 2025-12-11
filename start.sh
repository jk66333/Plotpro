#!/bin/bash
# Stop existing process
pkill -9 -f gunicorn

# Go to folder
cd /var/www/plotpro || exit

# Activate Python Virtual Env
source venv/bin/activate

# Install requirements just in case
pip install -r requirements.txt

# Start Gunicorn in Background
echo "Starting Gunicorn..."
gunicorn --workers 3 --bind 127.0.0.1:8000 receipt_app:app --daemon

# Check if it is running
sleep 2
if pgrep -f gunicorn > /dev/null
then
    echo "✅ Success! Server is running."
else
    echo "❌ Failed to start. Showing logs:"
    # Try running in foreground to show error
    gunicorn --workers 3 --bind 127.0.0.1:8000 receipt_app:app
fi
