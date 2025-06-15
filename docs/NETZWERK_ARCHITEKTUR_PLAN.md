# 🌐 DA-KI Dashboard - Netzwerk-Architektur Plan

## 🎯 **Ziel-System: 10.1.1.110 (data-web-gui VM)**

### 📊 **Service-Port-Zuordnung**

| Service | Port | URL | Beschreibung | Status |
|---------|------|-----|--------------|--------|
| **Haupt-API Backend** | 8003 | http://10.1.1.110:8003 | FastAPI - Wachstumsprognose & Progress | 🔄 Geplant |
| **Frontend Dashboard** | 8054 | http://10.1.1.110:8054 | Dash GUI - Hauptanwendung | 🔄 Geplant |
| **Google Search API** | 8002 | http://10.1.1.110:8002 | Externe Marktdaten | 🔄 Optional |
| **WebSocket Server** | 8765 | ws://10.1.1.110:8765 | Real-time Updates | 🔄 Optional |
| **Test & Monitoring** | 8055 | http://10.1.1.110:8055 | Test-Dashboard & Health Checks | 🔄 Geplant |

### 🔧 **Service-Details**

#### **1. Haupt-API Backend (Port 8003)**
```yaml
Service: api_top10_final.py (Demo-Version: api_demo.py)
Funktion: 
  - Wachstumsprognose Top 10
  - Progress API für Fortschrittsbalken
  - Firmensteckbriefe & Marktdaten
Endpoints:
  - GET /api/wachstumsprognose/top10
  - GET /api/calculation/progress
  - POST /api/wachstumsprognose/berechnen
Host: 0.0.0.0 (alle Interfaces)
Port: 8003
```

#### **2. Frontend Dashboard (Port 8054)**
```yaml
Service: dashboard_top10.py
Funktion:
  - Haupt-GUI für DA-KI Dashboard
  - Fortschrittsbalken-Anzeige
  - Wachstumsprognose-Visualisierung
  - Portfolio-Simulation
API-Verbindung: http://10.1.1.110:8003
Host: 0.0.0.0 (alle Interfaces)
Port: 8054
```

#### **3. Test & Monitoring Dashboard (Port 8055)**
```yaml
Service: test_dashboard_server.py (neu zu erstellen)
Funktion:
  - Service Health Checks
  - API Endpoint Tests
  - Netzwerk-Connectivity Tests
  - Performance Monitoring
  - Deployment Validation
Host: 0.0.0.0 (alle Interfaces)
Port: 8055
```

### 🚀 **Deployment-Strategie**

#### **Phase 1: Lokale Vorbereitung (Aktuell auf 10.1.1.105)**
- [x] Services entwickelt und getestet
- [x] API Demo funktional
- [x] Frontend Dashboard funktional
- [ ] Test-Dashboard erstellen

#### **Phase 2: Migration auf 10.1.1.110**
- [ ] SSH-Zugang zu 10.1.1.110 einrichten
- [ ] Projekt-Files übertragen
- [ ] Virtual Environment einrichten
- [ ] Services starten und konfigurieren

#### **Phase 3: Validierung & Tests**
- [ ] Netzwerk-Connectivity Tests
- [ ] API Endpoint Validierung
- [ ] Frontend-Backend Integration Test
- [ ] Performance & Load Tests

### 🔍 **Test-Matrix**

| Test-Kategorie | Endpoint/Service | Erwartetes Ergebnis | Test-Methode |
|----------------|------------------|---------------------|--------------|
| **API Health** | http://10.1.1.110:8003/ | {"status": "Running"} | curl GET |
| **Progress API** | http://10.1.1.110:8003/api/calculation/progress | Progress JSON | curl GET |
| **Growth API** | http://10.1.1.110:8003/api/wachstumsprognose/top10 | Top 10 Aktien JSON | curl GET |
| **Frontend** | http://10.1.1.110:8054 | Dashboard HTML | Browser/curl |
| **Test Dashboard** | http://10.1.1.110:8055 | Test Suite HTML | Browser/curl |
| **Integration** | Frontend → API | Daten werden geladen | Browser DevTools |

### 📋 **Netzwerk-Anforderungen**

#### **Firewall-Regeln für 10.1.1.110:**
```bash
# Eingehende Verbindungen
iptables -A INPUT -p tcp --dport 8003 -j ACCEPT  # API Backend
iptables -A INPUT -p tcp --dport 8054 -j ACCEPT  # Frontend Dashboard
iptables -A INPUT -p tcp --dport 8055 -j ACCEPT  # Test Dashboard
iptables -A INPUT -p tcp --dport 8002 -j ACCEPT  # Google Search API (optional)
iptables -A INPUT -p tcp --dport 8765 -j ACCEPT  # WebSocket Server (optional)
```

#### **DNS/Hosts-Einträge:**
```bash
# Optional: Für einfacheren Zugriff
10.1.1.110 da-ki-dashboard.local
10.1.1.110 da-ki-api.local
10.1.1.110 da-ki-test.local
```

### 🔄 **Service-Management**

#### **Start-Skripte:**
```bash
# /home/user/da-ki-dashboard/start_all_services.sh
#!/bin/bash
cd /home/user/da-ki-dashboard

# API Backend starten
python3 api_demo.py > logs/api.log 2>&1 &
echo $! > logs/api.pid

# Frontend Dashboard starten  
python3 frontend/dashboard_top10.py > logs/frontend.log 2>&1 &
echo $! > logs/frontend.pid

# Test Dashboard starten
python3 test_dashboard_server.py > logs/test.log 2>&1 &
echo $! > logs/test.pid

echo "✅ Alle DA-KI Services gestartet auf 10.1.1.110"
```

#### **Stop-Skripte:**
```bash
# /home/user/da-ki-dashboard/stop_all_services.sh
#!/bin/bash
cd /home/user/da-ki-dashboard/logs

# Services stoppen
kill $(cat api.pid frontend.pid test.pid) 2>/dev/null
rm -f *.pid

echo "🛑 Alle DA-KI Services gestoppt"
```

### 📈 **Monitoring & Health Checks**

#### **Service Health Endpoints:**
- **API Health**: `GET http://10.1.1.110:8003/health`
- **Frontend Health**: `GET http://10.1.1.110:8054/_dash-layout`
- **Test Dashboard Health**: `GET http://10.1.1.110:8055/health`

#### **Automated Health Checks:**
```bash
# /home/user/da-ki-dashboard/health_check.sh
#!/bin/bash
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://10.1.1.110:8003/)
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://10.1.1.110:8054/)

if [ "$API_STATUS" = "200" ] && [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✅ DA-KI Dashboard: All services healthy"
    exit 0
else
    echo "❌ DA-KI Dashboard: Service issues detected"
    echo "API: $API_STATUS, Frontend: $FRONTEND_STATUS"
    exit 1
fi
```

### 🚨 **Troubleshooting**

#### **Häufige Probleme:**
1. **Port bereits belegt**: `netstat -tulpn | grep :8054`
2. **IP-Binding Fehler**: Services auf `0.0.0.0` binden
3. **API nicht erreichbar**: Firewall-Regeln prüfen
4. **Frontend lädt nicht**: API-URLs in Frontend prüfen

#### **Debug-Befehle:**
```bash
# Service-Status prüfen
ps aux | grep python3 | grep da-ki

# Port-Status prüfen
netstat -tulpn | grep -E "(8003|8054|8055)"

# Log-Files prüfen
tail -f logs/*.log
```