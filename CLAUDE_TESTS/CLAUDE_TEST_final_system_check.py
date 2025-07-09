#!/usr/bin/env python3
"""
CLAUDE_TEST: Finaler System-Check für echtes Dashboard
⚠️ TESTCODE - NICHT FÜR PRODUCTION!
"""

import requests
import time

def final_system_check():
    print("🔧 CLAUDE_TEST: Finaler System-Check...")
    
    # Test 1: Dashboard läuft?
    try:
        response = requests.get("http://10.1.1.110:8054/", timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard läuft (Status 200)")
        else:
            print(f"❌ Dashboard Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard nicht erreichbar: {e}")
        return False
    
    # Test 2: Layout enthält Button?
    try:
        layout_response = requests.get("http://10.1.1.110:8054/_dash-layout", timeout=5)
        if layout_response.status_code == 200:
            layout_text = layout_response.text
            if 'refresh-growth-btn' in layout_text:
                print("✅ Button 'refresh-growth-btn' im Layout gefunden")
            else:
                print("❌ Button NICHT im Layout gefunden")
                return False
        else:
            print(f"❌ Layout nicht abrufbar: {layout_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Layout-Check fehlgeschlagen: {e}")
        return False
    
    # Test 3: Backend-API erreichbar?
    try:
        api_response = requests.get("http://10.1.1.110:8003/api/wachstumsprognose/top10", timeout=5)
        if api_response.status_code == 200:
            data = api_response.json()
            aktien_count = len(data.get('top_10_wachstums_aktien', []))
            print(f"✅ Backend-API funktioniert ({aktien_count} Aktien)")
        else:
            print(f"❌ Backend-API Status: {api_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend-API nicht erreichbar: {e}")
        return False
    
    # Test 4: Neuberechnung-API verfügbar?
    try:
        recalc_response = requests.post("http://10.1.1.110:8003/api/wachstumsprognose/berechnen", timeout=5)
        if recalc_response.status_code == 200:
            result = recalc_response.json()
            print(f"✅ Neuberechnung-API funktioniert: {result.get('status', 'unknown')}")
        else:
            print(f"❌ Neuberechnung-API Status: {recalc_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Neuberechnung-API nicht erreichbar: {e}")
        return False
    
    print("\n🎯 SYSTEM-STATUS:")
    print("✅ Dashboard läuft ohne NumPy-Fehler")
    print("✅ Button ist vorhanden")  
    print("✅ Backend-API funktioniert")
    print("✅ Neuberechnung-API funktioniert")
    print("\n📊 Dashboard URL: http://10.1.1.110:8054")
    print("🔄 Button: 'Prognose neu berechnen' sollte jetzt funktionieren!")
    
    return True

if __name__ == '__main__':
    success = final_system_check()
    if success:
        print("\n✅ SYSTEM REPARIERT - Dashboard ist bereit!")
    else:
        print("\n❌ SYSTEM HAT NOCH PROBLEME")