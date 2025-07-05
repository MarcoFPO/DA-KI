# DA-KI Services-Konfiguration

## Übersicht

Nach dem Basis-Setup werden alle Services für die DA-KI Anwendung konfiguriert:
- PostgreSQL (Database)
- Redis (Cache)
- nginx (Web Server)
- Python Environment

## 1. PostgreSQL-Konfiguration

### 1.1 Deutsche Lokalisierung
```bash
# PostgreSQL-Version ermitteln
POSTGRES_VERSION=$(ls /etc/postgresql/ | head -1)
echo "PostgreSQL Version: $POSTGRES_VERSION"

# Deutsche Lokalisierung für PostgreSQL
sudo -u postgres initdb --locale=de_DE.UTF-8 --encoding=UTF8 2>/dev/null || true
```

### 1.2 Benutzer und Datenbank erstellen
```bash
# PostgreSQL-Benutzer und Datenbank erstellen
sudo -u postgres psql -c "CREATE USER daki WITH PASSWORD 'daki2024';"
sudo -u postgres psql -c "CREATE DATABASE daki OWNER daki ENCODING 'UTF8' LC_COLLATE='de_DE.UTF-8' LC_CTYPE='de_DE.UTF-8';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE daki TO daki;"
```

### 1.3 PostgreSQL für LXC optimieren
```bash
# PostgreSQL-Konfiguration erweitern
cat >> /etc/postgresql/$POSTGRES_VERSION/main/postgresql.conf << 'EOF'
# DA-KI LXC-Optimierungen
listen_addresses = '10.1.1.110'
max_connections = 50
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100

# Deutsche Lokalisierung
lc_messages = 'de_DE.UTF-8'
lc_monetary = 'de_DE.UTF-8'
lc_numeric = 'de_DE.UTF-8'
lc_time = 'de_DE.UTF-8'
EOF
```

### 1.4 Zugriffsrechte konfigurieren
```bash
# Host-based Authentication für DA-KI
echo "host    daki    daki    10.1.1.110/32    md5" >> /etc/postgresql/$POSTGRES_VERSION/main/pg_hba.conf

# PostgreSQL neu starten
systemctl restart postgresql

# Verbindungstest
psql -h 10.1.1.110 -U daki -d daki -c "SELECT current_database(), version();"
```

## 2. Redis-Konfiguration

### 2.1 Redis für LXC optimieren
```bash
# Redis-Konfiguration überschreiben
cat > /etc/redis/redis.conf << 'EOF'
# DA-KI Redis-Konfiguration
bind 10.1.1.110
port 6379
requirepass daki2024

# Memory-Optimierungen für Container
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000

# Sicherheit
protected-mode yes
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""

# Logging
logfile /var/log/redis/redis-server.log
loglevel notice

# Persistence
dir /var/lib/redis
dbfilename daki.rdb
EOF
```

### 2.2 Redis starten und testen
```bash
# Redis neu starten
systemctl restart redis-server

# Redis-Verbindungstest
redis-cli -h 10.1.1.110 -a daki2024 ping

# Test-Daten setzen und abrufen
redis-cli -h 10.1.1.110 -a daki2024 set test_deutsch "Hallo DA-KI"
redis-cli -h 10.1.1.110 -a daki2024 get test_deutsch
```

## 3. nginx-Konfiguration

### 3.1 Haupt-Konfiguration
```bash
# nginx Haupt-Konfiguration optimieren
cat > /etc/nginx/nginx.conf << 'EOF'
user www-data;
worker_processes auto;
pid /run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    # Basic Settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;
    
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    
    # Gzip Settings
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Server Configs
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
EOF
```

### 3.2 DA-KI Site-Konfiguration
```bash
# DA-KI nginx Site-Konfiguration
cat > /etc/nginx/sites-available/daki << 'EOF'
server {
    listen 10.1.1.110:80;
    server_name 10.1.1.110;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Frontend (React Build)
    location / {
        root /var/www/daki-frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://10.1.1.110:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings
        proxy_connect_timeout 5s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF
```

### 3.3 nginx aktivieren
```bash
# Site aktivieren
ln -s /etc/nginx/sites-available/daki /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Konfiguration testen
nginx -t

# nginx neu starten
systemctl restart nginx

# Test-Seite für Frontend erstellen
cat > /var/www/daki-frontend/index.html << 'EOF'
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DA-KI - Deutsche Aktienanalyse</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; text-align: center; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .status { background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .info { background: #e8f4f8; padding: 20px; border-radius: 8px; margin: 20px 0; }
        h1 { color: #2c3e50; }
        .timestamp { font-size: 0.9em; color: #7f8c8d; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 DA-KI</h1>
        <h2>Deutsche Aktienanalyse mit KI</h2>
        <div class="status">
            <h3>✅ System Status</h3>
            <p>✅ nginx läuft</p>
            <p>✅ Frontend bereit</p>
            <p>🔧 Backend wird konfiguriert...</p>
        </div>
        <div class="info">
            <h3>📊 Projekt-Info</h3>
            <p>Privates Lernprojekt für deutsche Aktienanalyse</p>
            <p>Tech-Stack: Python FastAPI, React, PostgreSQL, Redis</p>
            <p>5-Faktor Scoring System für Aktienanalyse</p>
        </div>
        <div class="timestamp">
            Installation: $(date '+%d.%m.%Y %H:%M:%S')
        </div>
    </div>
</body>
</html>
EOF

# Test-Seite Berechtigung
chown www-data:www-data /var/www/daki-frontend/index.html
```

## 4. Python Environment

### 4.1 Virtual Environment erstellen
```bash
# Python Virtual Environment als daki-User
sudo -u daki python3 -m venv /opt/daki/venv
sudo -u daki /opt/daki/venv/bin/pip install --upgrade pip
```

### 4.2 Python-Pakete installieren
```bash
# DA-KI Python-Pakete installieren
sudo -u daki /opt/daki/venv/bin/pip install \
  fastapi \
  uvicorn[standard] \
  psycopg2-binary \
  redis \
  pandas \
  numpy \
  yfinance \
  python-multipart \
  jinja2 \
  python-dotenv \
  requests \
  matplotlib \
  seaborn \
  scikit-learn \
  python-dateutil \
  babel \
  pytz
```

### 4.3 Environment-Variablen
```bash
# Environment-Datei mit deutschen Einstellungen
cat > /opt/daki/.env << 'EOF'
# Database
DATABASE_URL=postgresql://daki:daki2024@10.1.1.110:5432/daki
REDIS_URL=redis://:daki2024@10.1.1.110:6379

# API
API_HOST=10.1.1.110
API_PORT=8000

# Localization
LANG=de_DE.UTF-8
LC_ALL=de_DE.UTF-8
TZ=Europe/Berlin

# Application
APP_NAME=DA-KI
APP_VERSION=1.0.0
DEBUG=false
EOF

# Berechtigung setzen
chown daki:daki /opt/daki/.env
chmod 600 /opt/daki/.env
```

## 5. Supervisor-Konfiguration

### 5.1 Supervisor für Process Management
```bash
# Supervisor-Konfiguration für DA-KI
cat > /etc/supervisor/conf.d/daki.conf << 'EOF'
[program:daki-api]
command=/opt/daki/venv/bin/uvicorn main:app --host 10.1.1.110 --port 8000 --workers 2
directory=/opt/daki/app
user=daki
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/daki/logs/api.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=3
environment=LANG=de_DE.UTF-8,LC_ALL=de_DE.UTF-8,TZ=Europe/Berlin

[program:daki-scheduler]
command=/opt/daki/venv/bin/python scheduler.py
directory=/opt/daki/app
user=daki
autostart=false
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/daki/logs/scheduler.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=3
environment=LANG=de_DE.UTF-8,LC_ALL=de_DE.UTF-8,TZ=Europe/Berlin
EOF

# Supervisor neu laden (später, wenn App vorhanden)
# supervisorctl reread
# supervisorctl update
```

## 6. Logrotation

### 6.1 DA-KI Logs
```bash
# Logrotate-Konfiguration für DA-KI
cat > /etc/logrotate.d/daki << 'EOF'
/opt/daki/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 daki daki
    postrotate
        supervisorctl restart daki-api || true
        supervisorctl restart daki-scheduler || true
    endscript
}
EOF
```

### 6.2 nginx Logs
```bash
# nginx Logrotation anpassen
cat > /etc/logrotate.d/nginx << 'EOF'
/var/log/nginx/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    prerotate
        if [ -d /etc/logrotate.d/httpd-prerotate ]; then \
            run-parts /etc/logrotate.d/httpd-prerotate; \
        fi \
    endscript
    postrotate
        systemctl reload nginx
    endscript
}
EOF
```

## 7. Service-Validierung

### 7.1 Alle Services prüfen
```bash
# Service-Status prüfen
systemctl status postgresql redis-server nginx supervisor

# Port-Bindings validieren
ss -tlnp | grep 10.1.1.110
netstat -tlnp | grep 10.1.1.110
```

### 7.2 Verbindungstests
```bash
# PostgreSQL-Verbindung
psql -h 10.1.1.110 -U daki -d daki -c "SELECT current_timestamp, version();"

# Redis-Verbindung
redis-cli -h 10.1.1.110 -a daki2024 ping
redis-cli -h 10.1.1.110 -a daki2024 info memory

# nginx-Test
curl -I http://10.1.1.110/
curl http://10.1.1.110/health
```

## 8. Nächste Schritte

Nach erfolgreicher Service-Konfiguration:

1. **Tests und Validierung** → [03-tests-validierung.md](03-tests-validierung.md)
2. **Entwicklungsumgebung** → [../04-entwicklung/01-entwicklungsumgebung.md](../04-entwicklung/01-entwicklungsumgebung.md)

## Checkliste

- [ ] PostgreSQL läuft auf 10.1.1.110:5432
- [ ] Redis läuft auf 10.1.1.110:6379
- [ ] nginx läuft auf 10.1.1.110:80
- [ ] Python Virtual Environment erstellt
- [ ] Alle Pakete installiert
- [ ] Environment-Variablen konfiguriert
- [ ] Supervisor konfiguriert
- [ ] Logrotation eingerichtet
- [ ] Test-Frontend erreichbar

---

**Status:** Services sind konfiguriert und bereit für Tests
