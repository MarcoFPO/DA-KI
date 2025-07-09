#!/usr/bin/env python3
"""
Debug: Dashboard-Inhalt überprüfen
Teste ob Live-Monitoring Sektion korrekt angezeigt wird
"""

import requests
import sys
import os
sys.path.append('/home/mdoehler/data-web-app/frontend')

from live_monitoring_module import create_live_monitoring_instance

def debug_dashboard_content():
    """Debug Dashboard-Inhalt"""
    
    print("🔍 Debug: Dashboard-Inhalt Überprüfung...")
    
    # Test 1: API-Verbindung
    print("\n1️⃣ API-Verbindung testen...")
    try:
        response = requests.get("http://localhost:8003/api/monitoring/summary", timeout=5)
        if response.status_code == 200:
            api_data = response.json()
            print(f"   ✅ API erreichbar: {api_data['total_positions']} Position(en)")
            print(f"   📊 Daten: {api_data}")
        else:
            print(f"   ❌ API-Fehler: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ API nicht erreichbar: {e}")
    
    # Test 2: Live-Monitoring Modul
    print("\n2️⃣ Live-Monitoring Modul testen...")
    try:
        live_monitoring = create_live_monitoring_instance()
        
        # API-Daten laden
        api_data = live_monitoring.load_api_portfolio_data()
        print(f"   ✅ Modul API-Daten: {api_data.get('total_positions', 0)} Position(en)")
        
        # Portfolio-Daten
        portfolio_data = live_monitoring.get_portfolio_data()
        print(f"   ✅ Portfolio-Daten: {portfolio_data['position_count']} Position(en)")
        
        # Slot-Daten
        slot_data = live_monitoring.get_slot_visual_data()
        print(f"   ✅ Slot-Daten: {slot_data['occupied_slots']}/5 belegt")
        
    except Exception as e:
        print(f"   ❌ Modul-Fehler: {e}")
    
    # Test 3: Dashboard URL testen
    print("\n3️⃣ Dashboard URL testen...")
    try:
        response = requests.get("http://10.1.1.110:8054", timeout=10)
        if response.status_code == 200:
            content = response.text
            print(f"   ✅ Dashboard erreichbar (Content-Length: {len(content)})")
            
            # Suche nach Live-Monitoring Inhalten
            if "Live-Monitoring" in content:
                print("   ✅ 'Live-Monitoring' Text gefunden")
            else:
                print("   ❌ 'Live-Monitoring' Text NICHT gefunden")
                
            if "Portfolio-Plätze" in content:
                print("   ✅ 'Portfolio-Plätze' Text gefunden")
            else:
                print("   ❌ 'Portfolio-Plätze' Text NICHT gefunden")
                
            if "AAPL" in content:
                print("   ✅ 'AAPL' gefunden")
            else:
                print("   ❌ 'AAPL' NICHT gefunden")
                
        else:
            print(f"   ❌ Dashboard nicht erreichbar: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Dashboard-Fehler: {e}")

if __name__ == "__main__":
    debug_dashboard_content()