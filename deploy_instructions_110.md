# 🚀 DA-KI Dashboard - Deployment Instructions für 10.1.1.110

## 📋 **Deployment-Status: SSH-Zugang erforderlich**

### ⚠️ **Aktuelle Situation:**
- ✅ Server 10.1.1.110 ist erreichbar (Port 22 offen)
- ❌ SSH-Authentifizierung fehlt (Permission denied)
- ✅ Deployment-Package vorbereitet
- ✅ Alle Services konfiguriert für 10.1.1.110

### 🔧 **Erforderliche Schritte für echtes Deployment:**

#### **Schritt 1: SSH-Zugang einrichten**
```bash
# Option A: SSH-Key kopieren (wenn Password-Auth aktiv)
ssh-copy-id mdoehler@10.1.1.110

# Option B: SSH-Key manuell hinzufügen
# 1. Auf 10.1.1.110 einloggen (über Console/VNC)
# 2. SSH-Verzeichnis erstellen:
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# 3. Public Key hinzufügen:
echo "SSH_PUBLIC_KEY_HIER" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Option C: Password-Authentication aktivieren
# Auf 10.1.1.110: sudo nano /etc/ssh/sshd_config
# PasswordAuthentication yes
# sudo systemctl restart ssh
```

#### **Schritt 2: Automatisches Deployment ausführen**
```bash
# Nach SSH-Zugang verfügbar:
cd /home/mdoehler/data-web-app
./migrate_to_110.sh
```

### 🔄 **Alternative: Manuelles Deployment**

Falls SSH-Automatisierung nicht möglich ist, hier die manuellen Schritte:

#### **Schritt 1: Package übertragen**
```bash
# Package erstellen
cd /home/mdoehler
tar -czf da-ki-dashboard-manual.tar.gz \
    --exclude='*.log' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='venv' \
    data-web-app/

# Package auf USB/Netzlaufwerk kopieren und auf 10.1.1.110 übertragen
```

#### **Schritt 2: Auf 10.1.1.110 installieren**
```bash
# Auf 10.1.1.110 ausführen:
cd /home/mdoehler
tar -xzf da-ki-dashboard-manual.tar.gz
mv data-web-app da-ki-dashboard

# Virtual Environment erstellen
cd da-ki-dashboard
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install fastapi uvicorn dash plotly pandas requests flask

# Log-Verzeichnis erstellen
mkdir -p logs
```

#### **Schritt 3: Services starten**
```bash
# API Backend starten (Port 8003)
nohup python3 api_demo.py > logs/api.log 2>&1 &
echo $! > logs/api.pid

# Frontend Dashboard starten (Port 8054)
nohup python3 frontend/dashboard_top10.py > logs/frontend.log 2>&1 &
echo $! > logs/frontend.pid

# Test Dashboard starten (Port 8055)
nohup python3 test_dashboard_server.py > logs/test.log 2>&1 &
echo $! > logs/test.pid
```

#### **Schritt 4: Services validieren**
```bash
# Service-Status prüfen
ps aux | grep python3 | grep -E "(api_demo|dashboard_top10|test_dashboard)"

# Ports prüfen
netstat -tulpn | grep -E "(8003|8054|8055)"

# HTTP-Tests
curl http://10.1.1.110:8003/
curl http://10.1.1.110:8054/
curl http://10.1.1.110:8055/health
```

### 📊 **Nach Deployment verfügbare URLs:**
- 🚀 **API Backend**: http://10.1.1.110:8003
- 📱 **Frontend Dashboard**: http://10.1.1.110:8054
- 🧪 **Test Dashboard**: http://10.1.1.110:8055

### 🧪 **Automatische Post-Deployment Tests:**
```bash
# Vollständiges Testprotokoll generieren
cd da-ki-dashboard
python3 generate_test_report.py

# Test Dashboard für kontinuierliches Monitoring nutzen
# URL: http://10.1.1.110:8055
```

### 🔧 **Service-Management nach Deployment:**

#### **Services stoppen:**
```bash
cd /home/mdoehler/da-ki-dashboard
kill $(cat logs/api.pid logs/frontend.pid logs/test.pid)
rm logs/*.pid
```

#### **Services neu starten:**
```bash
cd /home/mdoehler/da-ki-dashboard
./deploy_local_demo.sh  # Verwendet automatisch 10.1.1.110 Konfiguration
```

#### **Logs überwachen:**
```bash
# Live-Logs anzeigen
tail -f logs/*.log

# Fehler-Logs prüfen
grep -i error logs/*.log
```

### 📋 **Firewall-Konfiguration (falls erforderlich):**
```bash
# Auf 10.1.1.110 ausführen:
sudo ufw allow 8003/tcp  # API Backend
sudo ufw allow 8054/tcp  # Frontend Dashboard
sudo ufw allow 8055/tcp  # Test Dashboard
sudo ufw reload
```

### ✅ **Deployment-Validierung:**
Nach erfolgreichem Deployment sollten alle Tests im Test Dashboard (Port 8055) grün anzeigen:
- ✅ API Backend erreichbar
- ✅ Frontend Dashboard lädt
- ✅ Progress API antwortet
- ✅ Wachstumsprognose API funktional
- ✅ Frontend-Backend Integration

### 🚨 **Troubleshooting:**
- **Port bereits belegt**: `netstat -tulpn | grep 8054`
- **Service startet nicht**: `cat logs/frontend.log`
- **API nicht erreichbar**: Firewall-Regeln prüfen
- **Frontend lädt nicht**: Browser-Cache leeren

---

**📞 Support**: Bei Problemen Test Dashboard URL nutzen: http://10.1.1.110:8055