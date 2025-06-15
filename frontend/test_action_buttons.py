#!/usr/bin/env python3
"""
Test-Script: Überprüfung der Action-Buttons in der Dashboard-Tabelle
"""

import requests
import time
from bs4 import BeautifulSoup

def test_action_buttons():
    print("🧪 TEST: Action-Buttons in Detaillierte Wachstumsprognose Tabelle")
    print("=" * 70)
    
    # Dashboard-URL
    dashboard_url = "http://10.1.1.110:8054"
    
    try:
        # HTTP Request zum Dashboard
        print(f"\n📡 Teste Dashboard-Zugriff: {dashboard_url}")
        response = requests.get(dashboard_url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ HTTP Status: {response.status_code} OK")
            print(f"✅ Response Time: {response.elapsed.total_seconds():.3f}s")
            
            # HTML Content analysieren
            html_content = response.text
            
            # Suche nach Action-Spalte Header
            if "🎯 Aktion" in html_content:
                print("✅ Action-Spalte Header '🎯 Aktion' gefunden")
            else:
                print("❌ Action-Spalte Header '🎯 Aktion' NICHT gefunden")
            
            # Suche nach Live-Monitoring Buttons
            if "📊 Zu Live-Monitoring" in html_content:
                print("✅ Live-Monitoring Buttons gefunden")
            else:
                print("❌ Live-Monitoring Buttons NICHT gefunden")
            
            # Suche nach Button-IDs
            if "add-to-monitoring-btn" in html_content:
                print("✅ Button-IDs für Action-Buttons gefunden")
            else:
                print("❌ Button-IDs für Action-Buttons NICHT gefunden")
                
            # Suche nach Tabelle Header
            if "Detaillierte Wachstumsprognose mit Firmenprofilen" in html_content:
                print("✅ Korrekte Tabellen-Überschrift gefunden")
            else:
                print("❌ Tabellen-Überschrift NICHT korrekt")
            
            # Zähle Action-Buttons
            button_count = html_content.count("add-to-monitoring-btn")
            print(f"📊 Anzahl Action-Buttons gefunden: {button_count}")
            
            if button_count == 10:
                print("✅ Alle 10 Action-Buttons vorhanden (korrekt)")
            elif button_count > 0:
                print(f"⚠️  Nur {button_count}/10 Action-Buttons gefunden")
            else:
                print("❌ KEINE Action-Buttons gefunden!")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Fehler beim Dashboard-Test: {e}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_action_buttons()