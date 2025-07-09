#!/bin/bash
echo "🛠️ DA-KI Development Setup"
echo "=========================="

# 1. Erstelle notwendige Verzeichnisse
echo "📁 Erstelle Verzeichnisse..."
mkdir -p data logs certs config

# 2. Erstelle dev_secrets.json falls nicht vorhanden
if [ ! -f "config/dev_secrets.json" ]; then
    echo "🔐 Erstelle dev_secrets.json..."
    cat > config/dev_secrets.json << 'EOF'
{
  "database": {
    "url": "sqlite:///./data/daki.db"
  },
  "jwt": {
    "secret_key": "dev-secret-key-change-in-production",
    "access_token_expire_minutes": 30,
    "refresh_token_expire_days": 7
  },
  "api_keys": {
    "alpha_vantage": "demo",
    "yahoo_finance": "demo",
    "fred": "demo"
  },
  "users": {
    "admin": {
      "username": "admin",
      "password": "admin123"
    }
  },
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": true
  }
}
EOF
    echo "✅ dev_secrets.json erstellt"
else
    echo "✅ dev_secrets.json bereits vorhanden"
fi

# 3. Erstelle SSL-Zertifikate für Development
if [ ! -f "certs/server.crt" ]; then
    echo "🔒 Erstelle Development SSL-Zertifikate..."
    openssl req -x509 -newkey rsa:4096 -keyout certs/server.key -out certs/server.crt \
        -days 365 -nodes -subj "/C=DE/ST=NRW/L=City/O=DA-KI/OU=Dev/CN=localhost"
    echo "✅ SSL-Zertifikate erstellt"
else
    echo "✅ SSL-Zertifikate bereits vorhanden"
fi

# 4. Installiere Dependencies
echo "📦 Installiere Dependencies..."
./install_missing_deps.sh

# 5. Database Setup
echo "🗄️ Database Setup..."
python3 src/database/db_migration.py

# 6. Teste Installation
echo "🧪 Teste Installation..."
python3 -c "
try:
    from src.main_improved import app
    print('✅ Backend erfolgreich')
except Exception as e:
    print(f'❌ Backend Fehler: {e}')

try:
    from src.frontend.dashboard_app import create_daki_dashboard_app
    print('✅ Frontend erfolgreich')
except Exception as e:
    print(f'❌ Frontend Fehler: {e}')
"

echo ""
echo "🎉 Development Setup abgeschlossen!"
echo "🚀 Starte mit: python3 src/main_integrated.py"
echo "📊 Dashboard: http://localhost:8000/dashboard"
echo "🔧 API Docs: http://localhost:8000/api/docs"