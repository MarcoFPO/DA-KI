#!/usr/bin/env python3
"""
Debug-Test für Button-Funktionalität
"""

import sys
import os
sys.path.append('/home/mdoehler/data-web-app/frontend')

from ki_wachstumsprognose_module import KIWachstumsprognoseModule

def test_api_connection():
    print("🔧 Teste API-Verbindung...")
    
    # Test 1: Wachstumsprognose-Modul initialisieren
    wachstums_modul = KIWachstumsprognoseModule()
    print("✅ Wachstumsprognose-Modul initialisiert")
    
    # Test 2: Normale Daten laden
    print("\n📊 Teste normale Datenabfrage...")
    aktien_daten = wachstums_modul.get_aktien_daten()
    print(f"✅ {len(aktien_daten)} Aktien geladen")
    if aktien_daten:
        erste_aktie = aktien_daten[0]
        print(f"   Erste Aktie: {erste_aktie.get('symbol')} - {erste_aktie.get('name')}")
    
    # Test 3: Neuberechnung triggern
    print("\n🔄 Teste Prognose-Neuberechnung...")
    try:
        recalc_result = wachstums_modul.trigger_prognose_recalculation()
        print(f"✅ Neuberechnung: {recalc_result}")
        
        if recalc_result['success']:
            print("   ✅ API-Call erfolgreich!")
        else:
            print(f"   ⚠️ API-Antwort: {recalc_result['message']}")
    except Exception as e:
        print(f"   ❌ Fehler: {str(e)}")
    
    # Test 4: Progress abfragen
    print("\n📈 Teste Progress-Abfrage...")
    try:
        progress = wachstums_modul.get_calculation_progress()
        print(f"✅ Progress: {progress}")
    except Exception as e:
        print(f"   ❌ Fehler: {str(e)}")
    
    print("\n🎯 Test abgeschlossen!")

if __name__ == '__main__':
    test_api_connection()