#!/bin/bash
# 🚀 DA-KI Auto-Deployment Script für Server 10.1.1.110

echo "🚀 DA-KI Deployment auf Server 10.1.1.110 gestartet..."
echo "=================================================="

# Prüfe ob wir auf dem richtigen Server sind
CURRENT_IP=$(hostname -I | awk '{print $1}')
if [ "$CURRENT_IP" != "10.1.1.110" ]; then
    echo "⚠️  WARNUNG: Aktuell auf IP $CURRENT_IP"
    echo "📋 Dieses Script ist für Server 10.1.1.110 vorgesehen"
    echo ""
    echo "📦 Transfer-Anweisungen:"
    echo "scp mdoehler@10.1.1.105:/home/mdoehler/da-ki-project-20250614-195010.tar.gz /home/mdoehler/"
    echo "cd /home/mdoehler && tar -xzf da-ki-project-20250614-195010.tar.gz"
    echo ""
    read -p "Trotzdem fortfahren? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Setup Virtual Environment
echo "🐍 Virtual Environment Setup..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual Environment erstellt"
else
    echo "✅ Virtual Environment bereits vorhanden"
fi

# Aktiviere Virtual Environment
source venv/bin/activate

# Install Dependencies
echo "📦 Dependencies Installation..."
pip install --quiet --upgrade pip

# Core dependencies
pip install --quiet "numpy<2.0"
pip install --quiet pandas fastapi uvicorn dash plotly requests

# Additional dependencies
pip install --quiet websockets aioredis redis asyncio

# Optional dependencies
pip install --quiet python-dotenv schedule

echo "✅ Alle Dependencies installiert"

# Prüfe Konfiguration
echo "🔍 Konfiguration prüfen..."
echo "API_BASE_URL sollte 10.1.1.110:8003 enthalten:"
grep -n "API_BASE_URL" frontend/dashboard_top10.py | head -1

echo "✅ Konfiguration geprüft"

# Stoppe laufende Services
echo "🛑 Stoppe laufende Services..."
pkill -f "api_top10_final.py" 2>/dev/null || true
pkill -f "dashboard_top10.py" 2>/dev/null || true
sleep 2

echo "✅ Services gestoppt"

# Erstelle Startup Scripts
cat > start_api.sh << 'EOF'
#!/bin/bash
cd /home/mdoehler/data-web-app
source venv/bin/activate
echo "🚀 Starte API Backend auf 10.1.1.110:8003..."
python api/api_top10_final.py
EOF

cat > start_frontend.sh << 'EOF'
#!/bin/bash
cd /home/mdoehler/data-web-app
source venv/bin/activate
echo "🚀 Starte Frontend Dashboard auf 10.1.1.110:8054..."
python frontend/dashboard_top10.py
EOF

chmod +x start_api.sh
chmod +x start_frontend.sh

echo "✅ Startup Scripts erstellt"

# Starte Services
echo "🚀 Starte Services..."

# API Backend im Hintergrund
./start_api.sh > api_deployment.log 2>&1 &
API_PID=$!
echo "🔧 API Backend gestartet (PID: $API_PID)"

# Kurz warten
sleep 5

# Frontend im Hintergrund  
./start_frontend.sh > frontend_deployment.log 2>&1 &
FRONTEND_PID=$!
echo "🔧 Frontend Dashboard gestartet (PID: $FRONTEND_PID)"

# Warte auf Startup
echo "⏳ Warte auf Service-Startup..."
sleep 10

# Teste Services
echo "🧪 Teste Services..."

# API Test
if curl -f http://10.1.1.110:8003/api/calculation/progress --connect-timeout 5 > /dev/null 2>&1; then
    echo "✅ API Backend erreichbar auf http://10.1.1.110:8003"
else
    echo "❌ API Backend nicht erreichbar"
fi

# Frontend Test (nur Port-Check)
if nc -z 10.1.1.110 8054 2>/dev/null; then
    echo "✅ Frontend Dashboard läuft auf http://10.1.1.110:8054"
else
    echo "❌ Frontend Dashboard nicht erreichbar"
fi

echo ""
echo "🎉 DEPLOYMENT ABGESCHLOSSEN!"
echo "=========================="
echo "📊 API Backend:      http://10.1.1.110:8003"
echo "🖥️  Frontend:         http://10.1.1.110:8054"
echo "📈 Progress API:      http://10.1.1.110:8003/api/calculation/progress"
echo ""
echo "📋 Logs verfügbar:"
echo "   API:      tail -f api_deployment.log"
echo "   Frontend: tail -f frontend_deployment.log"
echo ""
echo "🛑 Services stoppen:"
echo "   kill $API_PID $FRONTEND_PID"
echo ""
echo "✅ DA-KI ist jetzt bereit mit Fortschrittsanzeige!"