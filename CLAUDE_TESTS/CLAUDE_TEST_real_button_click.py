#!/usr/bin/env python3
"""
CLAUDE_TEST: Test echter Button-Klick im echten Dashboard
⚠️ TESTCODE - NICHT FÜR PRODUCTION!
"""

import requests
import json
import time

def test_real_button_click():
    print("🔧 CLAUDE_TEST: Teste echten Button-Klick...")
    
    # Test 1: Dashboard erreichbar?
    try:
        response = requests.get("http://10.1.1.110:8054/", timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard erreichbar")
        else:
            print(f"❌ Dashboard nicht erreichbar: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Dashboard-Verbindung fehlgeschlagen: {e}")
        return
    
    # Test 2: Simuliere Button-Klick
    try:
        # Dash Callback-Update simulieren
        update_data = {
            "outputs": [
                {"id": "growth-status", "property": "children"},
                {"id": "wachstums-karten", "property": "children"},
                {"id": "wachstums-ranking-chart", "property": "figure"},
                {"id": "rendite-prognose-chart", "property": "figure"},
                {"id": "prognose-tabelle", "property": "children"},
                {"id": "progress-container-real", "property": "style"},
                {"id": "progress-bar-real", "property": "style"},
                {"id": "progress-text-real", "property": "children"},
                {"id": "refresh-growth-btn", "property": "disabled"}
            ],
            "inputs": [
                {"id": "interval-component", "property": "n_intervals", "value": 0},
                {"id": "refresh-growth-btn", "property": "n_clicks", "value": 1}
            ]
        }
        
        print("🔄 Sende Button-Klick an Dashboard...")
        response = requests.post(
            "http://10.1.1.110:8054/_dash-update-component",
            json=update_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Button-Klick erfolgreich gesendet")
            result = response.json()
            print(f"📊 Response erhalten: {len(str(result))} Zeichen")
            
            # Prüfe auf Progress-Bar in Response
            response_str = str(result)
            if 'progress-container-real' in response_str:
                print("✅ Progress-Container in Response gefunden")
            else:
                print("❌ Progress-Container NICHT in Response")
                
            if 'Prognose wird neu berechnet' in response_str:
                print("✅ Progress-Text in Response gefunden")
            else:
                print("❌ Progress-Text NICHT in Response")
                
        else:
            print(f"❌ Button-Klick fehlgeschlagen: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Callback-Test fehlgeschlagen: {e}")
    
    # Test 3: API-Backend testen
    try:
        print("\n📡 Teste Backend-API...")
        api_response = requests.post("http://10.1.1.110:8003/api/wachstumsprognose/berechnen", timeout=5)
        if api_response.status_code == 200:
            print("✅ Backend-API funktioniert")
            print(f"   Response: {api_response.json()}")
        else:
            print(f"❌ Backend-API Fehler: {api_response.status_code}")
    except Exception as e:
        print(f"❌ Backend-API nicht erreichbar: {e}")

if __name__ == '__main__':
    test_real_button_click()