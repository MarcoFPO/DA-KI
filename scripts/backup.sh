#!/bin/bash
# DA-KI Backup Script

set -e

BACKUP_DIR="/opt/da-ki/backups"
DAILY_DIR="$BACKUP_DIR/daily"
WEEKLY_DIR="$BACKUP_DIR/weekly"
DB_FILE="/opt/da-ki/data/database.db"
CONFIG_DIR="/opt/da-ki/config"
LOG_FILE="/opt/da-ki/logs/backup.log"
DATE=$(date +%Y%m%d_%H%M%S)
WEEKDAY=$(date +%u)

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starte Backup-Prozess..."

# Tägliches DB-Backup
log "Erstelle tägliches Datenbank-Backup..."
sqlite3 "$DB_FILE" ".backup $DAILY_DIR/database_$DATE.db"
gzip "$DAILY_DIR/database_$DATE.db"

# Konfiguration sichern
log "Sichere Konfigurationsdateien..."
tar -czf "$DAILY_DIR/config_$DATE.tar.gz" -C "$CONFIG_DIR" .

# Wöchentliches Vollbackup (Sonntag)
if [ "$WEEKDAY" -eq 7 ]; then
    log "Erstelle wöchentliches Vollbackup..."
    tar -czf "$WEEKLY_DIR/full_backup_$DATE.tar.gz" \
        --exclude="/opt/da-ki/backups" \
        --exclude="/opt/da-ki/logs/*.log" \
        --exclude="/opt/da-ki/app/venv" \
        /opt/da-ki/
fi

# Alte Backups löschen (älter als 30 Tage)
log "Bereinige alte Backups..."
find "$DAILY_DIR" -name "*.gz" -mtime +30 -delete
find "$WEEKLY_DIR" -name "*.tar.gz" -mtime +90 -delete

log "Backup-Prozess abgeschlossen"