# Deployment Instructions

Follow these steps to deploy the **Project Layout Manager** changes to your Ubuntu server.

## 1. Connect to Server
SSH into your server (using the credentials from your Deployment Guide):
```bash
ssh -p 7576 root@103.138.96.171
```

## 2. Navigate to Project Directory
Depending on your setup (check `DEPLOYMENT_GUIDE.md` vs actual server), go to the app folder:
```bash
# Option A (Likely)
cd /var/www/plotpro

# Option B
cd /opt/receipt_app
```

## 3. Pull Latest Code
Get the changes I just pushed:
```bash
git pull origin main
```

## 4. Install Dependencies
Update libraries including `psutil`:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 5. Database Migration (Critical)
Run this one-liner to add the `layout_svg_path` column to the `projects` table:
```bash
python3 -c "import database; conn=database.get_db_connection(); c=conn.cursor(); c.execute('ALTER TABLE projects ADD COLUMN IF NOT EXISTS layout_svg_path VARCHAR(255) DEFAULT NULL'); conn.commit(); print('Migration Successful');"
```

## 6. Create Service (If "Unit receipt_app.service not found")
If you get an error saying the service is not found, creates it:

1.  Create the file:
    ```bash
    sudo nano /etc/systemd/system/receipt_app.service
    ```
2.  Paste this content (adjust User/Group/Path if needed):
    ```ini
    [Unit]
    Description=Gunicorn instance to serve Receipt App
    After=network.target

    [Service]
    User=root
    Group=www-data
    WorkingDirectory=/var/www/plotpro
    Environment="PATH=/var/www/plotpro/venv/bin"
    ExecStart=/var/www/plotpro/venv/bin/gunicorn --workers 3 --bind unix:receipt_app.sock -m 007 receipt_app:app

    [Install]
    WantedBy=multi-user.target
    ```
3.  Load and Start:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl start receipt_app
    sudo systemctl enable receipt_app
    ```

## 7. Restart Service (If already exists)
Apply the changes:
```bash
sudo systemctl restart receipt_app
```

Your feature is now live!
