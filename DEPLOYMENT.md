# DA-KI Deployment Anleitung

## Debian Server Vollständige Einrichtung

### Voraussetzungen
- Debian 12 (Bookworm) LXC Container
- 4 CPU Kerne, 8GB RAM, 100GB SSD
- Statische IP: 10.1.1.180/24
- Gateway: 10.1.1.254
- DNS: 10.1.1.254

### 1. Basis-System Setup

```bash
# Als root ausführen
chmod +x deployment/debian_setup.sh
./deployment/debian_setup.sh
```

### 2. DA-KI Anwendung installieren

```bash
# Als da-ki Benutzer
su - da-ki
cd /opt/da-ki/app

# Repository klonen
git clone https://github.com/MarcoFPO/DA-KI.git .

# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
```

### 3. Konfiguration

```bash
# Secrets-Datei erstellen
cp config/secrets.env.template config/secrets.env
nano config/secrets.env  # API-Keys eintragen

# SSL-Zertifikat erstellen
./scripts/create_ssl.sh

# Konfiguration anpassen
nano config/config.yaml  # Bei Bedarf anpassen
```

### 4. Services installieren

```bash
# Als root
# Systemd Services
cp deployment/systemd/*.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable da-ki.service da-ki-redirect.service

# Cron Jobs
cp deployment/cron/da-ki /etc/cron.d/
chmod 644 /etc/cron.d/da-ki

# Log Rotation
cp deployment/logrotate/da-ki /etc/logrotate.d/
chmod 644 /etc/logrotate.d/da-ki
```

### 5. Datenbank initialisieren

```bash
# Als da-ki Benutzer
cd /opt/da-ki/app
source venv/bin/activate
python -m src.database.db_setup
```

### 6. System starten

```bash
# Als root
systemctl start da-ki.service
systemctl start da-ki-redirect.service

# Status prüfen
systemctl status da-ki.service
journalctl -u da-ki.service -f
```

### 7. Zugriff testen

- Web-Interface: `https://10.1.1.180`
- API: `https://10.1.1.180/api/`
- Health Check: `https://10.1.1.180/health`

### Verzeichnisstruktur

```
/opt/da-ki/
├── app/                 # Anwendungscode
│   ├── src/            # Python Quellcode
│   ├── venv/           # Virtual Environment
│   └── main.py         # Haupt-Server
├── data/               # SQLite Datenbank
├── config/             # Konfigurationsdateien
├── certs/              # SSL-Zertifikate
├── logs/               # Log-Dateien
├── scripts/            # Automatisierungs-Scripts
└── backups/            # Backup-Daten
```

### Troubleshooting

**Service startet nicht:**
```bash
journalctl -u da-ki.service -n 50
```

**Port 80/443 belegt:**
```bash
netstat -tulpn | grep :80
netstat -tulpn | grep :443
```

**SSL-Zertifikat Probleme:**
```bash
openssl x509 -in /opt/da-ki/certs/server.crt -text -noout
```

**Netzwerk testen:**
```bash
curl -k https://10.1.1.180/health
```