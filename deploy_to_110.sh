#!/bin/bash
# Deployment Script für Server 10.1.1.110

echo "🚀 DA-KI Dashboard Deployment für 10.1.1.110"

# Kopiere Dashboard-Datei
echo "📁 Kopiere dashboard_top10.py..."
scp frontend/dashboard_top10.py root@10.1.1.110:/root/

# SSH-Befehle für Installation
echo "🔧 Führe Installation auf 10.1.1.110 aus..."
ssh root@10.1.1.110 << 'EOF'
# Stoppe alte Prozesse
pkill -f dashboard_top10

# Starte neues Flask-Dashboard
cd /root
nohup python3 dashboard_top10.py > dashboard.log 2>&1 &

echo "✅ Dashboard gestartet auf http://10.1.1.110:8054"
EOF

echo "🎯 Deployment abgeschlossen!"