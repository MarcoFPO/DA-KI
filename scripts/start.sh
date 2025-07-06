#!/bin/bash
# DA-KI System Startup Script

set -e

LOG_FILE="/opt/da-ki/logs/startup.log"
CONFIG_FILE="/opt/da-ki/config/config.yaml"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "DA-KI System wird gestartet..."

# Verzeichnisse prüfen
log "Prüfe Verzeichnisstruktur..."
mkdir -p /opt/da-ki/{data,logs,backups/daily,backups/weekly}

# Virtual Environment aktivieren
log "Aktiviere Python Virtual Environment..."
source /opt/da-ki/app/venv/bin/activate

# Datenbankinitialisierung
log "Prüfe Datenbank..."
if [ ! -f "/opt/da-ki/data/database.db" ]; then
    log "Erstelle neue Datenbank..."
    python /opt/da-ki/app/src/database/db_setup.py
fi

# SSL-Zertifikate prüfen
log "Prüfe SSL-Zertifikate..."
if [ ! -f "/opt/da-ki/certs/server.crt" ]; then
    log "Erstelle SSL-Zertifikat..."
    /opt/da-ki/scripts/create_ssl.sh
fi

# Konfiguration validieren
log "Validiere Konfiguration..."
if [ ! -f "$CONFIG_FILE" ]; then
    log "FEHLER: Konfigurationsdatei nicht gefunden!"
    exit 1
fi

# Services starten
log "Starte DA-KI Services..."
systemctl start da-ki.service
systemctl start da-ki-redirect.service

# Status prüfen
sleep 5
if systemctl is-active --quiet da-ki.service; then
    log "DA-KI Service erfolgreich gestartet"
else
    log "FEHLER: DA-KI Service konnte nicht gestartet werden"
    journalctl -u da-ki.service --no-pager -n 20
    exit 1
fi

log "DA-KI System erfolgreich gestartet - https://10.1.1.180"