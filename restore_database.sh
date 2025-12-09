#!/bin/bash

################################################################################
# MySQL Database Restore Script
# For Receipt Management Application
#
# Usage:
#   ./restore_database.sh                    # Interactive mode
#   ./restore_database.sh /path/to/backup    # Direct restore
################################################################################

# Configuration
DB_NAME="receipt_app"
DB_USER="root"
DB_PASSWORD="List1you@"  # Change this to use environment variable in production
BACKUP_ROOT="/Users/admin/receipt_backups"

# MySQL paths (auto-detect or use default)
MYSQL_BIN="/usr/local/mysql-9.5.0-macos15-x86_64/bin"
MYSQL="$MYSQL_BIN/mysql"
MYSQLDUMP="$MYSQL_BIN/mysqldump"

# Fallback to PATH if custom location doesn't exist
if [ ! -f "$MYSQL" ]; then
    MYSQL="mysql"
fi
if [ ! -f "$MYSQLDUMP" ]; then
    MYSQLDUMP="mysqldump"
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

################################################################################
# List Available Backups
################################################################################

list_backups() {
    local backup_type=$1
    local backup_dir="$BACKUP_ROOT/$backup_type"
    
    if [ ! -d "$backup_dir" ]; then
        log_warning "No $backup_type backups found"
        return
    fi
    
    local backups=($(find "$backup_dir" -name "*.sql.gz" -type f | sort -r))
    
    if [ ${#backups[@]} -eq 0 ]; then
        log_warning "No $backup_type backups found"
        return
    fi
    
    echo ""
    echo -e "${GREEN}=== $backup_type Backups ===${NC}"
    
    local i=1
    for backup in "${backups[@]}"; do
        local filename=$(basename "$backup")
        local size=$(du -h "$backup" | cut -f1)
        local date=$(echo "$filename" | sed -E 's/.*([0-9]{8}_[0-9]{6}).*/\1/')
        local formatted_date=$(echo "$date" | sed -E 's/([0-9]{4})([0-9]{2})([0-9]{2})_([0-9]{2})([0-9]{2})([0-9]{2})/\1-\2-\3 \4:\5:\6/')
        
        echo -e "  ${BLUE}[$i]${NC} $formatted_date - $size - $filename"
        ((i++))
    done
}

################################################################################
# Interactive Backup Selection
################################################################################

select_backup() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   Database Backup Restore - Interactive Mode      ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # List all backup types
    list_backups "daily"
    list_backups "weekly"
    list_backups "monthly"
    list_backups "yearly"
    
    echo ""
    echo -e "${YELLOW}Enter the full path to the backup file you want to restore:${NC}"
    echo -e "${YELLOW}(or type 'cancel' to exit)${NC}"
    read -p "> " backup_path
    
    if [ "$backup_path" = "cancel" ]; then
        log_info "Restore cancelled by user"
        exit 0
    fi
    
    echo "$backup_path"
}

################################################################################
# Verify Backup File
################################################################################

verify_backup() {
    local backup_file=$1
    
    # Check if file exists
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    # Check if file is readable
    if [ ! -r "$backup_file" ]; then
        log_error "Cannot read backup file: $backup_file"
        return 1
    fi
    
    # Verify gzip integrity
    log_info "Verifying backup file integrity..."
    if ! gunzip -t "$backup_file" 2>/dev/null; then
        log_error "Backup file is corrupted or invalid!"
        return 1
    fi
    
    log_success "Backup file verified successfully"
    return 0
}

################################################################################
# Create Pre-Restore Backup
################################################################################

create_pre_restore_backup() {
    log_info "Creating pre-restore backup of current database..."
    
    local pre_restore_dir="$BACKUP_ROOT/pre_restore"
    mkdir -p "$pre_restore_dir"
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$pre_restore_dir/pre_restore_$timestamp.sql.gz"
    
    "$MYSQLDUMP" -u "$DB_USER" -p"$DB_PASSWORD" \
        --single-transaction \
        --routines \
        --triggers \
        --events \
        "$DB_NAME" 2>/dev/null | gzip > "$backup_file"
    
    if [ $? -eq 0 ]; then
        log_success "Pre-restore backup created: $backup_file"
        echo "$backup_file"
        return 0
    else
        log_error "Failed to create pre-restore backup"
        return 1
    fi
}

################################################################################
# Restore Database
################################################################################

restore_database() {
    local backup_file=$1
    
    log_info "Starting database restore process..."
    log_warning "This will REPLACE all current data in database: $DB_NAME"
    
    # Confirmation
    echo ""
    echo -e "${RED}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║              ⚠️  WARNING  ⚠️                        ║${NC}"
    echo -e "${RED}║  This will DELETE all current data and restore    ║${NC}"
    echo -e "${RED}║  from the selected backup file.                   ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    read -p "Are you sure you want to continue? (type 'YES' to confirm): " confirm
    
    if [ "$confirm" != "YES" ]; then
        log_info "Restore cancelled by user"
        exit 0
    fi
    
    # Create pre-restore backup
    local pre_restore_backup=$(create_pre_restore_backup)
    if [ $? -ne 0 ]; then
        log_error "Cannot proceed without pre-restore backup"
        exit 1
    fi
    
    # Drop and recreate database
    log_info "Dropping existing database..."
    "$MYSQL" -u "$DB_USER" -p"$DB_PASSWORD" -e "DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null
    
    log_info "Creating fresh database..."
    "$MYSQL" -u "$DB_USER" -p"$DB_PASSWORD" -e "CREATE DATABASE $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null
    
    # Restore from backup
    log_info "Restoring data from backup..."
    gunzip < "$backup_file" | "$MYSQL" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log_success "Database restored successfully!"
        
        # Verify restoration
        log_info "Verifying restoration..."
        local table_count=$("$MYSQL" -u "$DB_USER" -p"$DB_PASSWORD" -D "$DB_NAME" -e "SHOW TABLES;" 2>/dev/null | wc -l)
        log_info "Tables restored: $((table_count - 1))"
        
        echo ""
        echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║          ✓ Restore Completed Successfully         ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
        echo ""
        log_info "Pre-restore backup saved at: $pre_restore_backup"
        log_info "You can restore to this point if needed"
        
        return 0
    else
        log_error "Database restore failed!"
        log_warning "Attempting to restore from pre-restore backup..."
        
        # Restore from pre-restore backup
        "$MYSQL" -u "$DB_USER" -p"$DB_PASSWORD" -e "DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null
        "$MYSQL" -u "$DB_USER" -p"$DB_PASSWORD" -e "CREATE DATABASE $DB_NAME;" 2>/dev/null
        gunzip < "$pre_restore_backup" | "$MYSQL" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            log_success "Restored to pre-restore state"
        else
            log_error "CRITICAL: Failed to restore to pre-restore state!"
            log_error "Manual intervention required!"
        fi
        
        return 1
    fi
}

################################################################################
# Main Script
################################################################################

main() {
    # Check if backup file provided as argument
    if [ $# -eq 1 ]; then
        BACKUP_FILE=$1
    else
        # Interactive mode
        BACKUP_FILE=$(select_backup)
    fi
    
    # Verify backup file
    if ! verify_backup "$BACKUP_FILE"; then
        exit 1
    fi
    
    # Show backup details
    echo ""
    log_info "Backup file: $BACKUP_FILE"
    log_info "Size: $(du -h "$BACKUP_FILE" | cut -f1)"
    log_info "Target database: $DB_NAME"
    echo ""
    
    # Restore database
    restore_database "$BACKUP_FILE"
}

# Run main function
main "$@"
