#!/bin/bash
# SSL-Zertifikat erstellen

CERT_DIR="/opt/da-ki/certs"
LOG_FILE="/opt/da-ki/logs/ssl.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Erstelle SSL-Zertifikat für 10.1.1.180..."

mkdir -p "$CERT_DIR"
cd "$CERT_DIR"

# Self-signed Zertifikat erstellen
openssl req -x509 -newkey rsa:4096 \
    -keyout server.key \
    -out server.crt \
    -days 365 -nodes \
    -subj "/CN=10.1.1.180/O=DA-KI Stock Portfolio/C=DE/ST=Deutschland/L=Privat/emailAddress=admin@da-ki.local"

# Berechtigungen setzen
chown da-ki:da-ki server.key server.crt
chmod 600 server.key
chmod 644 server.crt

log "SSL-Zertifikat erfolgreich erstellt"