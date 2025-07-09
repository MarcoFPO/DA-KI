#!/bin/bash
echo "🔧 Installiere fehlende DA-KI Dependencies..."

# Prüfe ob Poetry verfügbar
if command -v poetry &> /dev/null; then
    echo "✅ Poetry gefunden - verwende Poetry"
    poetry install
else
    echo "⚠️ Poetry nicht gefunden - verwende pip"
    pip install passlib python-jose[cryptography] bcrypt
    pip install python-multipart aiofiles
    pip install dash plotly
fi

echo "✅ Dependencies installiert"
echo "🧪 Teste Backend..."
python3 -c "
try:
    from src.main_improved import app
    print('✅ Backend erfolgreich importiert')
except Exception as e:
    print(f'❌ Noch Fehler: {e}')
"