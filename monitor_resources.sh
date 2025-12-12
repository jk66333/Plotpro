#!/bin/bash

# Configuration
CPU_THRESHOLD=85
RAM_THRESHOLD=90
DISK_THRESHOLD=90
# Optional: Telegram/Slack Webhook URL
WEBHOOK_URL="" 
# Optional: Email to send alerts to (requires 'mail' utils installed)
EMAIL_TO=""

# Get Usage
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
RAM_USAGE=$(free | grep Mem | awk '{print $3/$2 * 100.0}')
DISK_USAGE=$(df -h / | grep / | awk '{ print $5 }' | sed 's/%//g')

# Log function
log_alert() {
    echo "$(date): ALERT - $1"
    
    # Example: Send to Telegram (if configured)
    if [ ! -z "$WEBHOOK_URL" ]; then
        curl -s -X POST -H 'Content-type: application/json' --data "{\"text\":\"🚨 Server Alert: $1\"}" "$WEBHOOK_URL"
    fi
}

# Checks
if (( $(echo "$CPU_USAGE > $CPU_THRESHOLD" | bc -l) )); then
    log_alert "High CPU Usage: ${CPU_USAGE}%"
fi

if (( $(echo "$RAM_USAGE > $RAM_THRESHOLD" | bc -l) )); then
    log_alert "High RAM Usage: ${RAM_USAGE}%"
fi

if [ "$DISK_USAGE" -gt "$DISK_THRESHOLD" ]; then
    log_alert "High Disk Usage: ${DISK_USAGE}%"
fi
