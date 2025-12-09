#!/bin/bash

################################################################################
# Backup System Setup Script
# Quick setup for database backup system
################################################################################

echo "╔════════════════════════════════════════════════════╗"
echo "║   Database Backup System - Quick Setup            ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
BACKUP_ROOT="/Users/admin/receipt_backups"
PROJECT_DIR="/Users/admin/receipt_app_project_autogravity_ws"

echo -e "${BLUE}Step 1:${NC} Creating backup directories..."
mkdir -p "$BACKUP_ROOT"/{daily,weekly,monthly,yearly,pre_restore}
echo -e "${GREEN}✓${NC} Backup directories created"

echo ""
echo -e "${BLUE}Step 2:${NC} Setting permissions..."
chmod +x "$PROJECT_DIR/backup_database.sh"
chmod +x "$PROJECT_DIR/restore_database.sh"
chmod 700 "$BACKUP_ROOT"
echo -e "${GREEN}✓${NC} Permissions set"

echo ""
echo -e "${BLUE}Step 3:${NC} Testing backup script..."
cd "$PROJECT_DIR"
./backup_database.sh

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Test backup successful!"
else
    echo -e "${YELLOW}⚠${NC} Test backup failed. Please check configuration."
    exit 1
fi

echo ""
echo -e "${BLUE}Step 4:${NC} Checking current backups..."
DAILY_COUNT=$(ls -1 "$BACKUP_ROOT/daily"/*.sql.gz 2>/dev/null | wc -l)
echo "  Daily backups: $DAILY_COUNT"
echo "  Total storage: $(du -sh $BACKUP_ROOT | cut -f1)"

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║          Setup Complete! ✓                         ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Schedule automated backups:"
echo "   crontab -e"
echo "   Add: 0 2 * * * $PROJECT_DIR/backup_database.sh"
echo ""
echo "2. Test restore:"
echo "   $PROJECT_DIR/restore_database.sh"
echo ""
echo "3. Read the guide:"
echo "   cat $PROJECT_DIR/BACKUP_GUIDE.md"
echo ""
echo "Backup location: $BACKUP_ROOT"
echo "Logs: $BACKUP_ROOT/backup.log"
