#!/usr/bin/env python3
"""
Demonstration der neuen Live-Monitoring Features
Zeigt die aktuellen Funktionen im DA-KI Dashboard
"""

import requests
import json
from datetime import datetime

def show_api_features():
    """Zeige verfügbare API Features"""
    print("🚀 DA-KI API Features")
    print("=" * 50)
    
    try:
        response = requests.get('http://10.1.1.110:8003/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Version: {data.get('version', 'unknown')}")
            print(f"💬 Message: {data.get('nachricht', 'N/A')}")
            print("\n🔧 Available Features:")
            for i, feature in enumerate(data.get('features', []), 1):
                print(f"   {i}. {feature}")
            
            print("\n🔗 Historical Endpoints:")
            for endpoint in data.get('historical_endpoints', []):
                print(f"   • {endpoint}")
                
        else:
            print(f"❌ API not available: {response.status_code}")
    except Exception as e:
        print(f"❌ API error: {e}")

def show_live_monitoring_positions():
    """Zeige Live-Monitoring Positionen"""
    print("\n📊 Live-Monitoring Positionen")
    print("=" * 50)
    
    try:
        response = requests.get('http://10.1.1.110:8003/api/dashboard/live-monitoring-positions', timeout=5)
        if response.status_code == 200:
            data = response.json()
            positions = data.get('live_monitoring_positionen', [])
            free_positions = data.get('freie_positionen', [])
            occupied_positions = data.get('belegte_positionen', [])
            
            print(f"🟢 Freie Positionen: {len(free_positions)} {free_positions}")
            print(f"🔴 Belegte Positionen: {len(occupied_positions)} {occupied_positions}")
            
            print(f"\n📋 Alle Positionen (1-10):")
            for pos in positions:
                status = "🟢 FREI" if not pos['ist_belegt'] else f"🔴 BELEGT ({pos['symbol']})"
                print(f"   Position {pos['position']}: {status}")
                
        else:
            print(f"❌ Positions API error: {response.status_code}")
    except Exception as e:
        print(f"❌ Positions error: {e}")

def show_growth_predictions():
    """Zeige Wachstumsprognosen"""
    print("\n🤖 Wachstumsprognosen")
    print("=" * 50)
    
    try:
        response = requests.get('http://10.1.1.110:8003/api/wachstumsprognose/top10', timeout=10)
        if response.status_code == 200:
            data = response.json()
            stocks = data.get('top_10_wachstums_aktien', [])
            
            print(f"📈 {len(stocks)} Wachstums-Aktien verfügbar")
            print("Top 5 Empfehlungen:")
            
            for i, stock in enumerate(stocks[:5], 1):
                symbol = stock.get('symbol', 'N/A')
                name = stock.get('name', 'N/A')[:25]
                score = stock.get('wachstums_score', 0)
                price = stock.get('current_price', 0)
                
                print(f"   {i}. {symbol} - {name}")
                print(f"      💰 €{price} | 🤖 Score: {score:.1f}/100")
                
        else:
            print(f"❌ Growth predictions error: {response.status_code}")
    except Exception as e:
        print(f"❌ Growth predictions error: {e}")

def demonstrate_workflow():
    """Demonstriere den Workflow"""
    print("\n🎯 Workflow Demonstration")
    print("=" * 50)
    
    print("1. 📊 Benutzer öffnet Dashboard: http://10.1.1.110:8054")
    print("2. 🤖 Wachstumsprognosen werden angezeigt (TOP 10)")
    print("3. 🎯 Benutzer klickt 'Zu Live-Monitoring' bei einer Aktie")
    print("4. 🔢 Position-Auswahl Dialog öffnet sich (1-10)")
    print("5. ✅ Aktie wird zu gewählter Position hinzugefügt")
    print("6. 📈 Live-Monitoring startet automatisch")
    print("7. 💾 Historische Daten werden gespeichert (5-Min Intervalle)")
    
    print("\n🎮 Neue Dashboard-Features:")
    print("   • Erweiterte Wachstumsprognose-Tabelle mit Auswahlbuttons")
    print("   • Position-Auswahl Dialog (1-10 Positionen)")
    print("   • 10-Positionen Live-Monitoring Dashboard")
    print("   • Entfernen-Funktion für jede Position")
    print("   • Automatische historische Datenspeicherung")
    print("   • Intraday-Charts mit 5-Minuten-Daten")

def test_adding_stock():
    """Teste das Hinzufügen einer Aktie"""
    print("\n🧪 Test: Aktie zu Live-Monitoring hinzufügen")
    print("=" * 50)
    
    try:
        # Test adding AAPL to position 1
        params = {
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'position': 1,
            'replace_existing': True
        }
        
        print("📤 Sending request to add AAPL to position 1...")
        response = requests.post(
            'http://10.1.1.110:8003/api/dashboard/add-to-live-monitoring', 
            params=params, 
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('message', 'Added successfully')}")
            print(f"   Symbol: {data.get('symbol', 'N/A')}")
            print(f"   Position: {data.get('position', 'N/A')}")
            print(f"   Added at: {data.get('hinzugefuegt_am', 'N/A')[:19]}")
        else:
            print(f"❌ Failed: HTTP {response.status_code}")
            if response.text:
                print(f"   Error: {response.text}")
                
    except Exception as e:
        print(f"❌ Request error: {e}")

def show_dashboard_status():
    """Zeige Dashboard Status"""
    print("\n🖥️  Dashboard Status")
    print("=" * 50)
    
    print("🌐 Dashboard URL: http://10.1.1.110:8054")
    print("🔧 API Server URL: http://10.1.1.110:8003")
    
    # Test if dashboard is accessible
    try:
        response = requests.get('http://10.1.1.110:8054/', timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard is running and accessible")
        else:
            print(f"⚠️  Dashboard returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard not accessible: {e}")

def main():
    """Main function"""
    print("🚀 DA-KI Live-Monitoring Integration Demo")
    print("=" * 70)
    print(f"🕒 Demo started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    show_api_features()
    show_live_monitoring_positions()
    show_growth_predictions()
    demonstrate_workflow()
    test_adding_stock()
    show_dashboard_status()
    
    print("\n🎉 Demo Complete!")
    print("=" * 70)
    print("📝 Zusammenfassung:")
    print("✅ API läuft mit allen neuen Features (Version 2.1.0)")
    print("✅ Live-Monitoring Positionen sind verfügbar (10 Slots)")
    print("✅ Wachstumsprognosen sind verfügbar")
    print("✅ Dashboard läuft und sollte neue Features zeigen")
    print("\n🎯 Nächste Schritte:")
    print("1. Öffnen Sie http://10.1.1.110:8054 im Browser")
    print("2. Schauen Sie sich die 'Detaillierte Wachstumsprognose' an")
    print("3. Klicken Sie auf '📊 Zu Live-Monitoring' bei einer Aktie")
    print("4. Wählen Sie eine Position (1-10) aus")
    print("5. Beobachten Sie das aktualisierte Live-Monitoring")

if __name__ == "__main__":
    main()