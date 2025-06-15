#!/bin/bash
# DA-KI Dashboard Migration Script
# Von 10.1.1.105 nach 10.1.1.110

set -e

echo "🚀 DA-KI Dashboard Migration zu 10.1.1.110"
echo "============================================"

# Konfiguration
SOURCE_DIR="/home/mdoehler/data-web-app"
TARGET_SERVER="10.1.1.110"
TARGET_USER="mdoehler"  # Anpassen falls nötig
TARGET_DIR="/home/$TARGET_USER/da-ki-dashboard"

# 1. Services auf aktueller Maschine stoppen
echo "🛑 Stoppe lokale Services..."
pkill -f "api_demo\|dashboard_top10\|test_dashboard" || true

# 2. Projekt-Konfiguration für 10.1.1.110 aktualisieren
echo "🔧 Aktualisiere Konfiguration für 10.1.1.110..."

# API Demo für 10.1.1.110 konfigurieren
sed -i 's/10\.1\.1\.105/10.1.1.110/g' api_demo.py
sed -i 's/localhost/10.1.1.110/g' api_demo.py

# Frontend für 10.1.1.110 konfigurieren  
sed -i 's/10\.1\.1\.105/10.1.1.110/g' frontend/dashboard_top10.py
sed -i 's/localhost/10.1.1.110/g' frontend/dashboard_top10.py

# Test Dashboard für 10.1.1.110 konfigurieren
sed -i 's/10\.1\.1\.105/10.1.1.110/g' test_dashboard_server.py
sed -i 's/localhost/10.1.1.110/g' test_dashboard_server.py

# 3. Deployment-Package erstellen
echo "📦 Erstelle Deployment-Package..."
cd ..
tar -czf da-ki-dashboard-110.tar.gz \
    --exclude='*.log' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='*.pyc' \
    data-web-app/

echo "✅ Package erstellt: da-ki-dashboard-110.tar.gz"

# 4. SSH-Verbindung testen
echo "🔗 Teste SSH-Verbindung zu $TARGET_SERVER..."
if ssh -o ConnectTimeout=10 $TARGET_USER@$TARGET_SERVER "echo 'SSH OK'"; then
    echo "✅ SSH-Verbindung erfolgreich"
else
    echo "❌ SSH-Verbindung fehlgeschlagen"
    echo "🔧 Bitte SSH-Zugang zu $TARGET_SERVER einrichten:"
    echo "   ssh-copy-id $TARGET_USER@$TARGET_SERVER"
    exit 1
fi

# 5. Package übertragen
echo "📤 Übertrage Package zu $TARGET_SERVER..."
scp da-ki-dashboard-110.tar.gz $TARGET_USER@$TARGET_SERVER:/tmp/

# 6. Remote-Installation
echo "🔧 Remote-Installation auf $TARGET_SERVER..."
ssh $TARGET_USER@$TARGET_SERVER << 'EOF'
set -e

echo "🔄 Extrahiere Package..."
cd /home/mdoehler
tar -xzf /tmp/da-ki-dashboard-110.tar.gz
rm -f /tmp/da-ki-dashboard-110.tar.gz

# Benenne Verzeichnis um
if [ -d "da-ki-dashboard" ]; then
    rm -rf da-ki-dashboard.backup
    mv da-ki-dashboard da-ki-dashboard.backup
fi
mv data-web-app da-ki-dashboard

echo "📂 Projekt installiert in: /home/mdoehler/da-ki-dashboard"

# Virtual Environment erstellen
echo "🐍 Erstelle Virtual Environment..."
cd da-ki-dashboard
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
echo "📦 Installiere Dependencies..."
pip install fastapi uvicorn dash plotly pandas requests flask

# Log-Verzeichnis erstellen
mkdir -p logs

# Startup-Skripte ausführbar machen
chmod +x *.sh || true

echo "✅ Installation abgeschlossen auf 10.1.1.110"
EOF

# 7. Services auf Ziel-Server starten
echo "🚀 Starte Services auf $TARGET_SERVER..."
ssh $TARGET_USER@$TARGET_SERVER << 'EOF'
cd /home/mdoehler/da-ki-dashboard

# Services starten
echo "🔧 Starte API Backend (Port 8003)..."
nohup python3 api_demo.py > logs/api.log 2>&1 &
echo $! > logs/api.pid

echo "🖥️ Starte Frontend Dashboard (Port 8054)..."  
nohup python3 frontend/dashboard_top10.py > logs/frontend.log 2>&1 &
echo $! > logs/frontend.pid

echo "🧪 Starte Test Dashboard (Port 8055)..."
nohup python3 test_dashboard_server.py > logs/test.log 2>&1 &
echo $! > logs/test.pid

echo "⏱️ Warte auf Service-Start..."
sleep 10

echo "🔍 Prüfe Service-Status..."
ps aux | grep python3 | grep -E "(api_demo|dashboard_top10|test_dashboard)" | grep -v grep || echo "⚠️ Einige Services möglicherweise nicht gestartet"

echo "✅ Services gestartet auf 10.1.1.110"
echo "📊 URLs:"
echo "   API Backend:      http://10.1.1.110:8003"
echo "   Frontend:         http://10.1.1.110:8054" 
echo "   Test Dashboard:   http://10.1.1.110:8055"
EOF

# 8. Post-Deployment Validierung
echo "🧪 Post-Deployment Tests..."
sleep 5

echo "🔍 Teste API Backend..."
if curl -s --connect-timeout 10 "http://$TARGET_SERVER:8003/" > /dev/null; then
    echo "✅ API Backend erreichbar"
else
    echo "❌ API Backend nicht erreichbar"
fi

echo "🔍 Teste Frontend Dashboard..."
if curl -s --connect-timeout 10 "http://$TARGET_SERVER:8054/" > /dev/null; then
    echo "✅ Frontend Dashboard erreichbar"
else
    echo "❌ Frontend Dashboard nicht erreichbar"
fi

echo "🔍 Teste Test Dashboard..."
if curl -s --connect-timeout 10 "http://$TARGET_SERVER:8055/health" > /dev/null; then
    echo "✅ Test Dashboard erreichbar"
else
    echo "❌ Test Dashboard nicht erreichbar"
fi

echo ""
echo "🎉 Migration abgeschlossen!"
echo "============================================"
echo "📊 DA-KI Dashboard URLs:"
echo "   🚀 API Backend:      http://10.1.1.110:8003"
echo "   📱 Frontend:         http://10.1.1.110:8054"
echo "   🧪 Test Dashboard:   http://10.1.1.110:8055"
echo ""
echo "🔄 Führe jetzt vollständiges Testprotokoll aus..."

# 9. Vollständiges Testprotokoll generieren
cd $SOURCE_DIR
python3 generate_test_report.py

echo "📋 Testprotokoll generiert - siehe docs/TESTPROTOKOLL_*.md"