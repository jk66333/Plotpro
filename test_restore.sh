#!/bin/bash

################################################################################
# Test Restore Script - Non-Interactive Demo
# Demonstrates restore functionality without user input
################################################################################

echo "╔════════════════════════════════════════════════════╗"
echo "║   Database Restore - Test Mode                    ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Configuration
BACKUP_ROOT="/Users/admin/receipt_backups"
DB_NAME="receipt_app"
DB_USER="root"
DB_PASSWORD="List1you@"

# MySQL paths
MYSQL_BIN="/usr/local/mysql-9.5.0-macos15-x86_64/bin"
MYSQL="$MYSQL_BIN/mysql"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Step 1:${NC} Listing available backups..."
echo ""

# List daily backups
echo -e "${GREEN}=== Daily Backups ===${NC}"
backups=($(find "$BACKUP_ROOT/daily" -name "*.sql.gz" -type f | sort -r))

if [ ${#backups[@]} -eq 0 ]; then
    echo "No backups found!"
    exit 1
fi

i=1
for backup in "${backups[@]}"; do
    filename=$(basename "$backup")
    size=$(du -h "$backup" | cut -f1)
    date=$(echo "$filename" | sed -E 's/.*([0-9]{8}_[0-9]{6}).*/\1/')
    formatted_date=$(echo "$date" | sed -E 's/([0-9]{4})([0-9]{2})([0-9]{2})_([0-9]{2})([0-9]{2})([0-9]{2})/\1-\2-\3 \4:\5:\6/')
    
    echo -e "  ${BLUE}[$i]${NC} $formatted_date - $size - $filename"
    ((i++))
done

echo ""
echo -e "${BLUE}Step 2:${NC} Verifying backup integrity..."

# Test the latest backup
LATEST_BACKUP="${backups[0]}"
echo "Testing: $(basename "$LATEST_BACKUP")"

if gunzip -t "$LATEST_BACKUP" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Backup file is valid and can be restored"
else
    echo -e "${YELLOW}✗${NC} Backup file is corrupted"
    exit 1
fi

echo ""
echo -e "${BLUE}Step 3:${NC} Checking database connection..."

if "$MYSQL" -u "$DB_USER" -p"$DB_PASSWORD" -e "SELECT 1;" 2>/dev/null >/dev/null; then
    echo -e "${GREEN}✓${NC} Database connection successful"
else
    echo -e "${YELLOW}✗${NC} Cannot connect to database"
    exit 1
fi

echo ""
echo -e "${BLUE}Step 4:${NC} Checking current database status..."

# Get current table count
TABLE_COUNT=$("$MYSQL" -u "$DB_USER" -p"$DB_PASSWORD" -D "$DB_NAME" -e "SHOW TABLES;" 2>/dev/null | wc -l)
TABLE_COUNT=$((TABLE_COUNT - 1))

echo "Current tables in database: $TABLE_COUNT"

# Get a sample of data
RECEIPT_COUNT=$("$MYSQL" -u "$DB_USER" -p"$DB_PASSWORD" -D "$DB_NAME" -e "SELECT COUNT(*) FROM receipts;" 2>/dev/null | tail -1)
echo "Current receipts in database: $RECEIPT_COUNT"

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║          Restore Test Summary                      ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}✓${NC} Found ${#backups[@]} backup(s)"
echo -e "${GREEN}✓${NC} Latest backup is valid"
echo -e "${GREEN}✓${NC} Database connection working"
echo -e "${GREEN}✓${NC} Current database has $TABLE_COUNT tables"
echo -e "${GREEN}✓${NC} Current database has $RECEIPT_COUNT receipts"
echo ""
echo -e "${BLUE}Restore capability:${NC} READY"
echo ""
echo "To perform an actual restore, run:"
echo "  ./restore_database.sh"
echo ""
echo "This will:"
echo "  1. Show all available backups"
echo "  2. Let you select which one to restore"
echo "  3. Create a safety backup before restoring"
echo "  4. Restore the selected backup"
echo "  5. Verify the restoration"
