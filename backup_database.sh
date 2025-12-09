#!/bin/bash

################################################################################
# MySQL Database Backup Script with Grandfather-Father-Son Retention
# For Receipt Management Application
#
# Backup Strategy:
# - Daily:   Last 7 days
# - Weekly:  Last 4 weeks (kept on Sundays)
# - Monthly: Last 12 months (kept on 1st of month)
# - Yearly:  Last 7 years (kept on Jan 1st)
################################################################################

# Configuration
DB_NAME="receipt_app"
DB_USER="root"
DB_PASSWORD="List1you@"  # Change this to use environment variable in production
BACKUP_ROOT="/Users/admin/receipt_backups"
LOG_FILE="$BACKUP_ROOT/backup.log"

# MySQL paths (auto-detect or use default)
MYSQL_BIN="/usr/local/mysql-9.5.0-macos15-x86_64/bin"
MYSQLDUMP="$MYSQL_BIN/mysqldump"

# Fallback to PATH if custom location doesn't exist
if [ ! -f "$MYSQLDUMP" ]; then
    MYSQLDUMP="mysqldump"
fi

# Backup directories
DAILY_DIR="$BACKUP_ROOT/daily"
WEEKLY_DIR="$BACKUP_ROOT/weekly"
MONTHLY_DIR="$BACKUP_ROOT/monthly"
YEARLY_DIR="$BACKUP_ROOT/yearly"

# Create directories if they don't exist
mkdir -p "$DAILY_DIR" "$WEEKLY_DIR" "$MONTHLY_DIR" "$YEARLY_DIR"

# Date variables
DATE=$(date +%Y%m%d_%H%M%S)
DAY_OF_WEEK=$(date +%u)  # 1=Monday, 7=Sunday
DAY_OF_MONTH=$(date +%d)
MONTH=$(date +%m)

# Backup filename
BACKUP_FILE="receipt_app_backup_$DATE.sql.gz"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Error handling
set -e
trap 'log "ERROR: Backup failed at line $LINENO"' ERR

################################################################################
# Main Backup Process
################################################################################

log "========================================="
log "Starting database backup process"
log "Database: $DB_NAME"
log "Backup file: $BACKUP_FILE"

# Create the backup
log "Creating database dump..."
"$MYSQLDUMP" -u "$DB_USER" -p"$DB_PASSWORD" \
    --single-transaction \
    --routines \
    --triggers \
    --events \
    --quick \
    --lock-tables=false \
    --set-gtid-purged=OFF \
    "$DB_NAME" 2>/dev/null | gzip > "$DAILY_DIR/$BACKUP_FILE"

# Verify backup was created
if [ ! -f "$DAILY_DIR/$BACKUP_FILE" ]; then
    log "ERROR: Backup file was not created!"
    exit 1
fi

BACKUP_SIZE=$(du -h "$DAILY_DIR/$BACKUP_FILE" | cut -f1)
log "Backup created successfully (Size: $BACKUP_SIZE)"

################################################################################
# Copy to Weekly Backup (if Sunday)
################################################################################

if [ "$DAY_OF_WEEK" -eq 7 ]; then
    log "Sunday detected - Creating weekly backup"
    cp "$DAILY_DIR/$BACKUP_FILE" "$WEEKLY_DIR/$BACKUP_FILE"
    log "Weekly backup created"
fi

################################################################################
# Copy to Monthly Backup (if 1st of month)
################################################################################

if [ "$DAY_OF_MONTH" -eq 01 ]; then
    log "First day of month - Creating monthly backup"
    cp "$DAILY_DIR/$BACKUP_FILE" "$MONTHLY_DIR/$BACKUP_FILE"
    log "Monthly backup created"
fi

################################################################################
# Copy to Yearly Backup (if January 1st)
################################################################################

if [ "$DAY_OF_MONTH" -eq 01 ] && [ "$MONTH" -eq 01 ]; then
    log "January 1st - Creating yearly backup"
    cp "$DAILY_DIR/$BACKUP_FILE" "$YEARLY_DIR/$BACKUP_FILE"
    log "Yearly backup created"
fi

################################################################################
# Cleanup Old Backups
################################################################################

log "Cleaning up old backups..."

# Keep only last 7 daily backups
log "Cleaning daily backups (keeping last 7)..."
find "$DAILY_DIR" -name "*.sql.gz" -type f -mtime +7 -delete
DAILY_COUNT=$(find "$DAILY_DIR" -name "*.sql.gz" -type f | wc -l)
log "Daily backups remaining: $DAILY_COUNT"

# Keep only last 4 weekly backups (28 days)
log "Cleaning weekly backups (keeping last 4 weeks)..."
find "$WEEKLY_DIR" -name "*.sql.gz" -type f -mtime +28 -delete
WEEKLY_COUNT=$(find "$WEEKLY_DIR" -name "*.sql.gz" -type f | wc -l)
log "Weekly backups remaining: $WEEKLY_COUNT"

# Keep only last 12 monthly backups (365 days)
log "Cleaning monthly backups (keeping last 12 months)..."
find "$MONTHLY_DIR" -name "*.sql.gz" -type f -mtime +365 -delete
MONTHLY_COUNT=$(find "$MONTHLY_DIR" -name "*.sql.gz" -type f | wc -l)
log "Monthly backups remaining: $MONTHLY_COUNT"

# Keep only last 7 yearly backups (2555 days ≈ 7 years)
log "Cleaning yearly backups (keeping last 7 years)..."
find "$YEARLY_DIR" -name "*.sql.gz" -type f -mtime +2555 -delete
YEARLY_COUNT=$(find "$YEARLY_DIR" -name "*.sql.gz" -type f | wc -l)
log "Yearly backups remaining: $YEARLY_COUNT"

################################################################################
# Calculate Total Storage Used
################################################################################

TOTAL_SIZE=$(du -sh "$BACKUP_ROOT" | cut -f1)
log "Total backup storage used: $TOTAL_SIZE"

################################################################################
# Backup Verification (Optional but Recommended)
################################################################################

log "Verifying backup integrity..."
if gunzip -t "$DAILY_DIR/$BACKUP_FILE" 2>/dev/null; then
    log "Backup integrity verified - file is valid"
else
    log "ERROR: Backup file is corrupted!"
    exit 1
fi

################################################################################
# Email Notification (Optional)
################################################################################

# Uncomment to enable email notifications
# if command -v mail &> /dev/null; then
#     echo "Backup completed successfully. Size: $BACKUP_SIZE, Total: $TOTAL_SIZE" | \
#         mail -s "Database Backup Success - $(date +%Y-%m-%d)" admin@yourdomain.com
# fi

################################################################################
# Summary
################################################################################

log "========================================="
log "Backup Summary:"
log "  Daily backups:   $DAILY_COUNT"
log "  Weekly backups:  $WEEKLY_COUNT"
log "  Monthly backups: $MONTHLY_COUNT"
log "  Yearly backups:  $YEARLY_COUNT"
log "  Total storage:   $TOTAL_SIZE"
log "Backup process completed successfully!"
log "========================================="

exit 0
