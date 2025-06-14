#!/usr/bin/env python3
"""
Remote Dashboard Deployment für 10.1.1.110
Da SSH nicht verfügbar ist, erstellen wir eine HTTP-basierte Deployment-Lösung
"""

import requests
import json

# Lese die Flask-Dashboard-Datei
with open('frontend/dashboard_top10.py', 'r') as f:
    dashboard_code = f.read()

# Erstelle Deployment-Payload
deployment_data = {
    'action': 'deploy_dashboard',
    'code': dashboard_code,
    'target_ip': '10.1.1.110',
    'target_port': 8054
}

print("🚀 Versuche Dashboard-Deployment auf 10.1.1.110...")

# Prüfe ob ein Management-Interface verfügbar ist
try:
    response = requests.get("http://10.1.1.110:8054/", timeout=5)
    print("📊 Zielserver ist erreichbar")
    print(f"   Status Code: {response.status_code}")
    print(f"   Content Length: {len(response.text)}")
    
    # Zeige aktuelle Inhalte
    if "DA-KI Dashboard" in response.text:
        print("   ✅ Flask Dashboard bereits vorhanden")
    elif "Deutsche Aktienanalyse" in response.text:
        print("   ⚠️ Altes Dash Dashboard läuft noch")
    else:
        print("   ❓ Unbekannter Inhalt")
        
except Exception as e:
    print(f"❌ Fehler beim Verbindungstest: {e}")

print("\n📋 Da SSH nicht verfügbar ist, müssen Sie manuell:")
print("1. Auf 10.1.1.110 einloggen")
print("2. Das alte Dashboard stoppen") 
print("3. Die neue dashboard_top10.py Datei dort platzieren")
print("4. Das neue Flask-Dashboard starten")

# Erstelle Ready-to-Deploy Datei
with open('dashboard_ready_for_110.py', 'w') as f:
    f.write(dashboard_code)
    
print("✅ Datei 'dashboard_ready_for_110.py' erstellt - bereit für manuelles Deployment")