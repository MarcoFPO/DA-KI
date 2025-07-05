# DA-KI Umgebungsplanung

## Architektur-Übersicht

### Monolithischer Ansatz (Gewählt)
```
┌─────────────────────────────────────┐
│ DA-KI All-in-One LXC Container      │
│ Static IP: 10.1.1.110               │
├─────────────────────────────────────┤
│ Port 80/443: nginx (Frontend)       │
│ Port 8000: FastAPI (Backend)        │
│ Port 5432: PostgreSQL (Database)    │
│ Port 6379: Redis (Cache)            │
│ Port 22: SSH (Management)           │
├─────────────────────────────────────┤
│ Services:                           │
│ - Python Backend (FastAPI)          │
│ - React Frontend (nginx)            │
│ - PostgreSQL Database               │
│ - Redis Cache                       │
│ - Cron Jobs (Data Collection)       │
│ - systemd Services                  │
└─────────────────────────────────────┘
```

**Vorteile dieser Architektur:**
- Einfache Verwaltung (ein Container)
- Keine Netzwerk-Komplexität
- Schnelle Entwicklung
- Ressourcenschonend

## Netzwerk-Konfiguration

### Spezifische Netzwerk-Details
- **IP-Adresse:** 10.1.1.110/24
- **Gateway:** 10.1.1.254
- **DNS:** 10.1.1.254
- **Firewall:** Deaktiviert

### Single-IP Setup
```
Internet/LAN
    │
    ├── Static IP (10.1.1.110)
    │   │
    │   ├── Port 22  → SSH Access
    │   ├── Port 80  → HTTP (nginx)
    │   ├── Port 443 → HTTPS (nginx)
    │   └── Port 8000 → API (optional, dev only)
    │
    └── DA-KI LXC Container
        ├── nginx (Frontend Proxy)
        ├── FastAPI (Backend)
        ├── PostgreSQL (Database)
        └── Redis (Cache)
```

### Service-Kommunikation (Intern)
```
Alle Services laufen auf derselben Static IP:
- nginx lauscht auf Port 80/443
- nginx proxied zu FastAPI auf Port 8000
- FastAPI verbindet zu PostgreSQL auf Port 5432
- FastAPI verbindet zu Redis auf Port 6379
- Alle Verbindungen über Static IP (keine localhost/127.0.0.1)
```

### Firewall-Regeln (Minimal)
```bash
# Erlaubte Ports von außen
22/tcp  → SSH Management
80/tcp  → HTTP
443/tcp → HTTPS

# Optional für Development
8000/tcp → Direct API Access

# Alle anderen Ports: Geschlossen
```

## Ressourcen-Planung

### Container-Spezifikationen
- **Container:** 1x LXC
- **CPU:** 4 Cores
- **RAM:** 6GB
- **Storage:** 30GB
- **Netzwerk:** 1 Static IP
- **Ports:** 22, 80, 443, 8000 (optional für API-Tests)

### LXC Container Layout
```
Container: da-ki (10.1.1.110)
├── RAM: 6GB
├── CPU: 4 Cores
├── Storage: 30GB
└── Services:
    ├── nginx: ~200MB RAM
    ├── FastAPI: ~500MB RAM
    ├── PostgreSQL: ~2GB RAM
    ├── Redis: ~512MB RAM
    └── System: ~1GB RAM
```

## Service-Konfiguration

### nginx-Konfiguration
```nginx
server {
    listen 10.1.1.110:80;
    server_name 10.1.1.110;
    
    # Frontend (React Build)
    location / {
        root /var/www/daki-frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://10.1.1.110:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Service-Binding (Wichtig!)
```bash
# PostgreSQL - Bind auf Static IP
listen_addresses = '10.1.1.110'

# Redis - Bind auf Static IP  
bind 10.1.1.110

# FastAPI - Bind auf Static IP
uvicorn main:app --host 10.1.1.110 --port 8000
```

### Environment-Variablen
```bash
# Verbindungen in der Anwendung:
DATABASE_URL=postgresql://daki:daki2024@10.1.1.110:5432/daki
REDIS_URL=redis://:daki2024@10.1.1.110:6379
API_HOST=10.1.1.110
API_PORT=8000
```

## Storage-Strategie

### Datenverteilung
```
/opt/daki/
├── app/           # Anwendungscode
├── data/          # Datenbank-Dumps
├── logs/          # Application Logs
├── backups/       # Backup-Dateien
└── venv/          # Python Virtual Environment

/var/lib/postgresql/  # PostgreSQL Data
/var/lib/redis/       # Redis Data
/var/www/daki-frontend/  # React Build
```

### Backup-Strategie
- **Proxmox Snapshots:** Täglich vor größeren Updates
- **Database Dumps:** Täglich um 2:00 Uhr
- **Application Backups:** Wöchentlich
- **Git Repository:** Bei jeder Code-Änderung

## Development vs. Production

### Vereinfachter Ansatz
```
Development = Production:
├── Ein LXC Container für alles
├── Alle Services in einem Container
├── Direkter Zugriff über Static IP
├── Proxmox Snapshots für Rollbacks
└── Einfache Wartung und Updates
```

### Deployment-Strategie
```
1. Lokale Entwicklung → Git Push
2. SSH in Container → Git Pull
3. Services neu starten → Tests
4. Proxmox Snapshot → Backup
```

## Monitoring und Logging

### Einfaches Monitoring
```bash
# System-Überwachung
htop                    # Resource Usage
systemctl status        # Service Status
journalctl -f           # Live Logs
df -h                   # Disk Usage
```

### Log-Dateien
```
/var/log/nginx/         # nginx Logs
/opt/daki/logs/         # Application Logs
/var/log/postgresql/    # PostgreSQL Logs
/var/log/redis/         # Redis Logs
journalctl              # systemd Logs
```

### Health-Check Script
```bash
#!/bin/bash
# Simple Health Check
curl -f http://10.1.1.110:8000/health || echo "API DOWN"
pg_isready -h 10.1.1.110 -p 5432 || echo "DB DOWN"
redis-cli -h 10.1.1.110 ping || echo "CACHE DOWN"
```

## Sicherheit

### Basis-Sicherheit
```bash
# SSH-Key Only (no password)
# Automatic Security Updates
# Firewall: nur notwendige Ports
# Regular Backups
# Non-root Application User
```

### SSL/TLS (Optional)
```bash
# Für Production:
# Let's Encrypt für HTTPS
# SSL-Zertifikat automatisch erneuern
# HTTP → HTTPS Redirect
```

## Wartung und Updates

### Regelmäßige Wartung
```bash
# System Updates (monatlich)
apt update && apt upgrade -y

# Log Rotation (automatisch)
logrotate /etc/logrotate.d/daki

# Backup Verification (wöchentlich)
./scripts/maintenance/verify-backups.sh

# Performance Check (bei Bedarf)
./scripts/maintenance/performance-check.sh
```

### Troubleshooting
```bash
# Service-Status prüfen
systemctl status postgresql redis-server nginx

# Port-Bindings prüfen
netstat -tlnp | grep 10.1.1.110

# Logs analysieren
journalctl -u daki-api -f
tail -f /opt/daki/logs/*.log

# Verbindungen testen
./scripts/maintenance/test-connections.sh
```

## Nächste Schritte

### Container-Vorbereitung
1. **LXC Container erstellen** mit Debian 12
2. **Netzwerk konfigurieren** (10.1.1.110)
3. **SSH-Zugang einrichten**
4. **Basis-Installation** durchführen

### Service-Setup
1. **PostgreSQL installieren** und konfigurieren
2. **Redis installieren** und konfigurieren
3. **nginx installieren** und konfigurieren
4. **Python Environment** einrichten

### Deployment-Vorbereitung
1. **Systemd Services** erstellen
2. **Backup-Skripte** einrichten
3. **Monitoring** konfigurieren
4. **Tests** durchführen

---

**Wichtiger Hinweis:** Alle Services müssen auf 10.1.1.110 binden - keine localhost/127.0.0.1 verwenden!
