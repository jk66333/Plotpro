# Database Backup Management Guide

## 📋 Backup Strategy Overview

### **Grandfather-Father-Son (GFS) Retention Policy**

```
┌─────────────────────────────────────────────────────────────┐
│                    Backup Retention Timeline                │
├─────────────────────────────────────────────────────────────┤
│ Daily Backups:    Last 7 days      (7 backups)             │
│ Weekly Backups:   Last 4 weeks     (4 backups)             │
│ Monthly Backups:  Last 12 months   (12 backups)            │
│ Yearly Backups:   Last 7 years     (7 backups)             │
├─────────────────────────────────────────────────────────────┤
│ Total Backups:    ~30 backups maximum                       │
│ Estimated Size:   ~300MB - 3GB (depending on data growth)  │
└─────────────────────────────────────────────────────────────┘
```

### **Why This Strategy?**

✅ **Compliance Ready:** Meets 7-year retention for financial records
✅ **Storage Efficient:** ~90% less storage than daily-only backups
✅ **Quick Recovery:** Recent backups for fast restoration
✅ **Cost Effective:** Minimal storage costs
✅ **Disaster Recovery:** Multiple recovery points

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Make Scripts Executable

```bash
cd /Users/admin/receipt_app_project_autogravity_ws

chmod +x backup_database.sh
chmod +x restore_database.sh
```

### Step 2: Create Backup Directory

```bash
mkdir -p /Users/admin/receipt_backups/{daily,weekly,monthly,yearly,pre_restore}
```

### Step 3: Test Backup Script

```bash
./backup_database.sh
```

You should see output like:
```
[2025-12-05 11:05:00] =========================================
[2025-12-05 11:05:00] Starting database backup process
[2025-12-05 11:05:00] Database: receipt_app
[2025-12-05 11:05:01] Backup created successfully (Size: 2.3M)
[2025-12-05 11:05:01] Backup process completed successfully!
```

### Step 4: Schedule Automated Backups

```bash
# Open crontab editor
crontab -e

# Add this line (runs daily at 2:00 AM)
0 2 * * * /Users/admin/receipt_app_project_autogravity_ws/backup_database.sh >> /Users/admin/receipt_backups/backup.log 2>&1
```

**Alternative times:**
- `0 2 * * *` - 2:00 AM daily (recommended)
- `0 3 * * *` - 3:00 AM daily
- `0 */6 * * *` - Every 6 hours
- `0 0,12 * * *` - Midnight and noon

---

## 📊 Backup Schedule Explained

### **How It Works:**

1. **Every Day at 2 AM:**
   - Creates a new backup in `daily/` folder
   - Deletes backups older than 7 days

2. **Every Sunday:**
   - Copies Sunday's backup to `weekly/` folder
   - Keeps last 4 weekly backups

3. **1st of Every Month:**
   - Copies that day's backup to `monthly/` folder
   - Keeps last 12 monthly backups

4. **January 1st:**
   - Copies that day's backup to `yearly/` folder
   - Keeps last 7 yearly backups

### **Example Timeline:**

```
Today: December 5, 2025

Daily Backups (7):
├── Dec 5 (today)
├── Dec 4
├── Dec 3
├── Dec 2
├── Dec 1
├── Nov 30
└── Nov 29

Weekly Backups (4):
├── Dec 1 (Sunday)
├── Nov 24 (Sunday)
├── Nov 17 (Sunday)
└── Nov 10 (Sunday)

Monthly Backups (12):
├── Dec 1, 2025
├── Nov 1, 2025
├── Oct 1, 2025
└── ... (back to Jan 1, 2025)

Yearly Backups (7):
├── Jan 1, 2025
├── Jan 1, 2024
├── Jan 1, 2023
└── ... (back to 2019)
```

---

## 🔄 Restore Procedures

### **Interactive Restore (Recommended)**

```bash
./restore_database.sh
```

This will:
1. Show all available backups
2. Let you select which one to restore
3. Create a safety backup before restoring
4. Verify the backup integrity
5. Restore the database

### **Direct Restore**

```bash
./restore_database.sh /path/to/backup/file.sql.gz
```

### **Common Restore Scenarios:**

#### **Scenario 1: Accidental Data Deletion (Today)**
```bash
# Restore from yesterday's backup
./restore_database.sh
# Select the most recent daily backup
```

#### **Scenario 2: Need Data from Last Week**
```bash
# Restore from last Sunday's backup
./restore_database.sh
# Select the appropriate weekly backup
```

#### **Scenario 3: Need Data from 6 Months Ago**
```bash
# Restore from monthly backup
./restore_database.sh
# Select the monthly backup from 6 months ago
```

#### **Scenario 4: Audit/Compliance (Need 3-year-old Data)**
```bash
# Restore from yearly backup
./restore_database.sh
# Select the yearly backup from 3 years ago
```

---

## 📈 Monitoring & Maintenance

### **Check Backup Status**

```bash
# View backup log
tail -50 /Users/admin/receipt_backups/backup.log

# Count backups in each category
echo "Daily: $(ls -1 /Users/admin/receipt_backups/daily/*.sql.gz 2>/dev/null | wc -l)"
echo "Weekly: $(ls -1 /Users/admin/receipt_backups/weekly/*.sql.gz 2>/dev/null | wc -l)"
echo "Monthly: $(ls -1 /Users/admin/receipt_backups/monthly/*.sql.gz 2>/dev/null | wc -l)"
echo "Yearly: $(ls -1 /Users/admin/receipt_backups/yearly/*.sql.gz 2>/dev/null | wc -l)"

# Check total storage used
du -sh /Users/admin/receipt_backups
```

### **Verify Latest Backup**

```bash
# Test the latest backup file
LATEST=$(ls -t /Users/admin/receipt_backups/daily/*.sql.gz | head -1)
gunzip -t "$LATEST" && echo "✓ Backup is valid" || echo "✗ Backup is corrupted"
```

### **Monthly Maintenance Checklist**

- [ ] Verify backups are running (check log file)
- [ ] Test restore from a recent backup
- [ ] Check storage space usage
- [ ] Verify backup file integrity
- [ ] Review backup retention counts

---

## 💾 Storage Estimates

### **Typical Storage Requirements:**

| Data Size | Daily (7) | Weekly (4) | Monthly (12) | Yearly (7) | Total |
|-----------|-----------|------------|--------------|------------|-------|
| 10 MB     | 70 MB     | 40 MB      | 120 MB       | 70 MB      | 300 MB |
| 50 MB     | 350 MB    | 200 MB     | 600 MB       | 350 MB     | 1.5 GB |
| 100 MB    | 700 MB    | 400 MB     | 1.2 GB       | 700 MB     | 3 GB   |
| 500 MB    | 3.5 GB    | 2 GB       | 6 GB         | 3.5 GB     | 15 GB  |

**Current Database Size:**
```bash
# Check current database size
mysql -u root -p -e "SELECT 
    table_schema AS 'Database',
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.tables 
WHERE table_schema = 'receipt_app'
GROUP BY table_schema;"
```

---

## 🔐 Security Best Practices

### **Encrypt Backups (Optional but Recommended)**

Add encryption to backup script:

```bash
# Encrypt backup
gpg --symmetric --cipher-algo AES256 backup.sql.gz

# Decrypt when restoring
gpg --decrypt backup.sql.gz.gpg | gunzip | mysql -u root -p receipt_app
```

### **Secure Backup Storage**

```bash
# Set restrictive permissions
chmod 700 /Users/admin/receipt_backups
chmod 600 /Users/admin/receipt_backups/*/*.sql.gz

# Only owner can read/write backups
```

### **Off-Site Backup (Highly Recommended)**

**Option 1: Cloud Storage (Google Drive, Dropbox)**
```bash
# Install rclone
brew install rclone

# Configure cloud storage
rclone config

# Sync backups to cloud
rclone sync /Users/admin/receipt_backups remote:receipt_backups
```

**Option 2: External Drive**
```bash
# Copy to external drive
rsync -av /Users/admin/receipt_backups /Volumes/ExternalDrive/backups/
```

**Option 3: Network Storage (NAS)**
```bash
# Mount network drive and copy
rsync -av /Users/admin/receipt_backups /mnt/nas/backups/
```

---

## 🚨 Disaster Recovery Plan

### **Complete System Failure**

1. **Install fresh system**
2. **Install MySQL**
3. **Restore from most recent backup:**
   ```bash
   mysql -u root -p -e "CREATE DATABASE receipt_app;"
   gunzip < backup_file.sql.gz | mysql -u root -p receipt_app
   ```
4. **Verify data integrity**
5. **Resume operations**

### **Ransomware Attack**

1. **Disconnect system immediately**
2. **Do NOT pay ransom**
3. **Restore from clean backup (before infection)**
4. **Scan system for malware**
5. **Change all passwords**
6. **Review security measures**

### **Data Corruption**

1. **Identify when corruption occurred**
2. **Restore from backup before corruption**
3. **Investigate root cause**
4. **Implement preventive measures**

---

## 📞 Troubleshooting

### **Problem: Backup Script Not Running**

```bash
# Check if cron is running
sudo launchctl list | grep cron

# Check cron logs
grep CRON /var/log/system.log

# Test script manually
./backup_database.sh
```

### **Problem: Backup File Corrupted**

```bash
# Test backup integrity
gunzip -t backup_file.sql.gz

# If corrupted, use previous backup
ls -lt /Users/admin/receipt_backups/daily/
```

### **Problem: Out of Disk Space**

```bash
# Check disk usage
df -h

# Clean old backups manually
find /Users/admin/receipt_backups/daily -name "*.sql.gz" -mtime +7 -delete

# Check backup sizes
du -sh /Users/admin/receipt_backups/*
```

### **Problem: Restore Failed**

```bash
# Check MySQL error log
tail -50 /usr/local/var/mysql/*.err

# Verify database exists
mysql -u root -p -e "SHOW DATABASES;"

# Try manual restore
gunzip < backup.sql.gz | mysql -u root -p receipt_app
```

---

## 📋 Backup Checklist

### **Daily (Automated)**
- [x] Backup runs at 2 AM
- [x] Backup file created successfully
- [x] Old backups cleaned up

### **Weekly**
- [ ] Check backup log for errors
- [ ] Verify backup file integrity
- [ ] Check storage space

### **Monthly**
- [ ] Test restore procedure
- [ ] Review backup retention
- [ ] Update documentation if needed
- [ ] Verify off-site backups

### **Quarterly**
- [ ] Full disaster recovery test
- [ ] Review and update recovery procedures
- [ ] Audit backup security
- [ ] Review storage costs

### **Yearly**
- [ ] Review backup strategy
- [ ] Update retention policy if needed
- [ ] Test all yearly backups
- [ ] Security audit

---

## 💡 Pro Tips

1. **Test Restores Regularly**
   - Monthly test restores ensure backups work
   - Practice makes perfect in emergencies

2. **Monitor Backup Sizes**
   - Sudden size changes indicate issues
   - Track growth for capacity planning

3. **Keep Multiple Copies**
   - 3-2-1 Rule: 3 copies, 2 different media, 1 off-site
   - Protects against multiple failure scenarios

4. **Document Everything**
   - Keep restore procedures updated
   - Document any custom configurations

5. **Automate Verification**
   - Add integrity checks to backup script
   - Alert on failures

---

## 📚 Additional Resources

- **MySQL Backup Documentation:** https://dev.mysql.com/doc/refman/8.0/en/backup-and-recovery.html
- **Disaster Recovery Planning:** https://www.ready.gov/business/implementation/IT
- **Data Retention Laws:** Consult with legal advisor for your jurisdiction

---

## 🆘 Emergency Contacts

**In case of data emergency:**

1. **Stop all operations immediately**
2. **Do not make changes to the database**
3. **Contact database administrator**
4. **Review backup logs**
5. **Follow disaster recovery plan**

**Emergency Restore Hotline:** [Your contact info]
**Database Administrator:** [Your contact info]
**IT Support:** [Your contact info]

---

## Summary

✅ **Automated daily backups**
✅ **Intelligent retention policy**
✅ **Easy restore procedures**
✅ **Disaster recovery ready**
✅ **Storage efficient**
✅ **Compliance ready (7 years)**

Your data is now protected with industry-standard backup practices!
