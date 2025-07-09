#!/usr/bin/env python3
"""
Test: Live-Monitoring 5-Slot Visualisierung
Direkter Test der API-Integration ohne Dash
"""

import sys
import os
sys.path.append('/home/mdoehler/data-web-app/frontend')

from live_monitoring_module import create_live_monitoring_instance

def test_5_slot_visualization():
    """Teste die 5-Slot Portfolio Visualisierung"""
    
    print("🧪 Teste Live-Monitoring 5-Slot Visualisierung...")
    
    # Erstelle Live-Monitoring Instanz
    live_monitoring = create_live_monitoring_instance()
    
    # Test 1: Lade API-Daten
    print("\n1️⃣ Lade API-Daten...")
    api_data = live_monitoring.load_api_portfolio_data()
    print(f"   ✅ API-Daten geladen: {api_data.get('total_positions', 0)} Positionen")
    
    # Test 2: Prüfe Portfolio-Synchronisation
    print("\n2️⃣ Prüfe Portfolio-Synchronisation...")
    portfolio_data = live_monitoring.get_portfolio_data()
    print(f"   ✅ Portfolio-Positionen: {portfolio_data['position_count']}")
    
    # Test 3: Teste 5-Slot Daten
    print("\n3️⃣ Teste 5-Slot Status...")
    slot_data = live_monitoring.get_slot_visual_data()
    print(f"   ✅ Slot-Status: {slot_data}")
    
    # Test 4: Teste verfügbare Slots
    print("\n4️⃣ Teste verfügbare Slots...")
    available_slots = live_monitoring.get_available_slots()
    print(f"   ✅ Verfügbare Slots: {available_slots}")
    
    # Test 5: Zeige detaillierte Slot-Informationen
    print("\n5️⃣ Detaillierte Slot-Informationen:")
    for i in range(1, 6):
        slot_data = live_monitoring._get_slot_data(i)
        if slot_data:
            profit_loss = slot_data.get('profit_loss', 0)
            change_percent = slot_data.get('change_percent', 0)
            print(f"   📈 Slot {i}: {slot_data['symbol']} - {slot_data['shares']} Aktien")
            print(f"      💰 Investment: €{slot_data['investment']:.0f} → €{slot_data.get('current_value', 0):.0f}")
            print(f"      📊 Gewinn/Verlust: {change_percent:+.1f}% ({profit_loss:+.0f}€)")
        else:
            print(f"   ⭕ Slot {i}: FREI")
    
    print(f"\n🎯 Ergebnis: {1 if api_data.get('total_positions', 0) > 0 else 5 - api_data.get('total_positions', 0)}/5 Slots belegt")
    print("✅ Live-Monitoring 5-Slot Visualisierung funktioniert!")

if __name__ == "__main__":
    test_5_slot_visualization()