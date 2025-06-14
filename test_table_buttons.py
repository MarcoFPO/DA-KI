#!/usr/bin/env python3
"""
Spezieller Test für die Tabelle mit Buttons
"""

import requests
import json

def test_dashboard():
    print("🧪 Teste Dashboard-Tabelle...")
    
    # 1. Teste API
    print("\n1. API Test:")
    try:
        response = requests.get("http://localhost:8003/api/wachstumsprognose/top10", timeout=10)
        if response.status_code == 200:
            data = response.json()
            stocks = data.get('top_10_wachstums_aktien', [])
            print(f"   ✅ API liefert {len(stocks)} Aktien")
        else:
            print(f"   ❌ API Fehler: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ API nicht erreichbar: {e}")
        return
    
    # 2. Teste Dashboard HTML
    print("\n2. Dashboard HTML Test:")
    try:
        response = requests.get("http://localhost:8054/", timeout=10)
        if response.status_code == 200:
            html = response.text
            print(f"   ✅ Dashboard antwortet (HTML-Größe: {len(html)} chars)")
            
            # Suche nach der Tabelle
            if "Detaillierte Wachstumsprognose" in html:
                print("   ✅ Tabellen-Titel gefunden")
            else:
                print("   ❌ Tabellen-Titel NICHT gefunden")
            
            # Suche nach Buttons
            if "Zu Live-Monitoring" in html:
                print("   ✅ Buttons GEFUNDEN!")
            else:
                print("   ❌ Buttons NICHT gefunden")
                
            # Suche nach der Version
            if "BUTTONS-FIXED" in html:
                print("   ✅ Neue Version bestätigt")
            else:
                print("   ❌ Alte Version läuft noch")
                
        else:
            print(f"   ❌ Dashboard Fehler: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Dashboard nicht erreichbar: {e}")
    
    # 3. Teste über die externe IP
    print("\n3. Externe IP Test:")
    try:
        response = requests.get("http://10.1.1.110:8054/", timeout=10)
        if response.status_code == 200:
            html = response.text
            print(f"   ✅ Externe IP antwortet (HTML-Größe: {len(html)} chars)")
            
            if "Zu Live-Monitoring" in html:
                print("   ✅ Buttons über externe IP GEFUNDEN!")
            else:
                print("   ❌ Buttons über externe IP NICHT gefunden")
        else:
            print(f"   ❌ Externe IP Fehler: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Externe IP nicht erreichbar: {e}")

if __name__ == "__main__":
    test_dashboard()