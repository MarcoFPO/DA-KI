#!/bin/bash

echo "🔄 Neustart der DA-KI Services mit noCache Headers"
echo "=================================================="

# Stop existing processes
echo "🛑 Stoppe laufende Services..."
pkill -f "api_top10_final.py"
pkill -f "dashboard_top10.py"
sleep 3

# Start API server with noCache
echo "🚀 Starte API Server mit noCache Headers..."
cd /home/mdoehler/data-web-app
./venv/bin/python api/api_top10_final.py > api_nocache.log 2>&1 &
API_PID=$!
echo "   API Server PID: $API_PID (Port 8003)"

# Wait for API to start
sleep 5

# Start Dashboard with noCache
echo "🖥️  Starte Dashboard mit noCache Headers..."
./venv/bin/python frontend/dashboard_top10.py > dashboard_nocache.log 2>&1 &
DASHBOARD_PID=$!
echo "   Dashboard PID: $DASHBOARD_PID (Port 8054)"

# Wait for services to start
sleep 5

echo ""
echo "✅ Services mit noCache Headers gestartet!"
echo ""
echo "📊 API Server:"
echo "   URL: http://localhost:8003"
echo "   Log: tail -f api_nocache.log"
echo ""
echo "🖥️  Dashboard:"
echo "   URL: http://localhost:8054"
echo "   Log: tail -f dashboard_nocache.log"
echo ""
echo "🧪 Testseite:"
echo "   file:///home/mdoehler/data-web-app/test_buttons.html"
echo ""

# Test if services are running
echo "🧪 Teste Services..."

# Test API
if curl -s http://localhost:8003/ > /dev/null 2>&1; then
    echo "✅ API Server läuft"
else
    echo "❌ API Server nicht erreichbar"
fi

# Test Dashboard
if curl -s http://localhost:8054/ > /dev/null 2>&1; then
    echo "✅ Dashboard läuft"
else
    echo "❌ Dashboard nicht erreichbar"
fi

echo ""
echo "🎯 Browser-Cache wird jetzt verhindert!"
echo "   Die neuen Features sollten sofort sichtbar sein."
echo ""
echo "📋 NoCache Headers hinzugefügt:"
echo "   ✅ Cache-Control: no-cache, no-store, must-revalidate"
echo "   ✅ Pragma: no-cache"
echo "   ✅ Expires: 0"
echo ""
echo "🔄 Öffnen Sie jetzt das Dashboard: http://localhost:8054"