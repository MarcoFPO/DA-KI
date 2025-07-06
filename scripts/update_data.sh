#!/bin/bash
# Tägliche Datenaktualisierung

set -e

LOG_FILE="/opt/da-ki/logs/update.log"
LOCKFILE="/tmp/da-ki-update.lock"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Lock-File prüfen (verhindert parallele Ausführung)
if [ -f "$LOCKFILE" ]; then
    log "Update läuft bereits (Lock-File vorhanden)"
    exit 1
fi

# Lock-File erstellen
touch "$LOCKFILE"
trap "rm -f $LOCKFILE" EXIT

log "Starte tägliche Datenaktualisierung..."

# Virtual Environment aktivieren
source /opt/da-ki/app/venv/bin/activate

# Python-Script für Datenupdate aufrufen
cd /opt/da-ki/app
python -c "
import sys
sys.path.append('src')
from plugins.plugin_manager import PluginManager
from services.analysis_service import AnalysisService
import asyncio

async def update_data():
    print('Aktualisiere Marktdaten...')
    # Plugin Manager initialisieren und Daten abrufen
    # Implementierung folgt in der nächsten Phase
    pass

asyncio.run(update_data())
"

log "Datenaktualisierung abgeschlossen"