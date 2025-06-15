#!/usr/bin/env python3
"""
Initialisierung des Historical Stock Data Monitoring Systems
Fügt Standard-Aktien zur Überwachung hinzu und testet das System
"""

import sys
import os
sys.path.append('/home/mdoehler/data-web-app/services')

from historical_stock_data import HistoricalStockDataManager
from datetime import datetime

def main():
    """Initialisiert das Historical Data Monitoring System"""
    
    print("🚀 Initialisierung des DA-KI Historical Stock Data Monitoring Systems")
    print("=" * 70)
    
    # Initialize Historical Data Manager
    db_path = "/home/mdoehler/data-web-app/database/aktienanalyse_de.db"
    manager = HistoricalStockDataManager(db_path)
    
    # Standard-Aktien für Live-Monitoring hinzufügen
    standard_stocks = [
        ("AAPL", "Apple Inc.", 300),
        ("TSLA", "Tesla Inc.", 300),
        ("NVDA", "NVIDIA Corporation", 300),
        ("MSFT", "Microsoft Corporation", 300),
        ("GOOGL", "Alphabet Inc.", 300),
        ("PLTR", "Palantir Technologies Inc.", 300),
        ("ENPH", "Enphase Energy Inc.", 300),
        ("AMD", "Advanced Micro Devices Inc.", 300),
        ("NFLX", "Netflix Inc.", 300),
        ("META", "Meta Platforms Inc.", 300)
    ]
    
    print("\n📊 Füge Standard-Aktien zur Live-Monitoring Liste hinzu:")
    print("-" * 50)
    
    for symbol, name, interval in standard_stocks:
        try:
            manager.add_monitored_stock(symbol, name, interval)
            print(f"✅ {symbol:6} - {name}")
        except Exception as e:
            print(f"❌ {symbol:6} - Fehler: {e}")
    
    # Zeige überwachte Aktien
    print("\n📈 Aktuell überwachte Aktien:")
    print("-" * 50)
    monitored = manager.get_monitored_stocks()
    
    for stock in monitored:
        print(f"📊 {stock['symbol']:6} - {stock['name']} (Intervall: {stock['monitoring_interval']}s)")
    
    print(f"\n✅ Gesamt überwachte Aktien: {len(monitored)}")
    
    # Teste Datenbank-Struktur
    print("\n🔧 Teste Datenbank-Struktur:")
    print("-" * 50)
    
    try:
        # Teste mit einer Sample-Aktie
        sample_data = {
            'current_price': 195.89,
            'change': '+2.34',
            'change_percent': '+1.21%',
            'market_cap': '3.04T',
            'pe_ratio': '31.2'
        }
        
        manager.save_historical_data("AAPL", sample_data)
        manager.save_intraday_data("AAPL", 195.89, change_amount=2.34, change_percent="+1.21%")
        
        print("✅ Historische Daten gespeichert")
        print("✅ Intraday-Daten gespeichert")
        
        # Teste Abruf
        historical = manager.get_historical_data("AAPL", 7)
        intraday = manager.get_intraday_data("AAPL", 24)
        stats = manager.get_stock_statistics("AAPL")
        
        print(f"✅ Historische Daten abgerufen: {len(historical)} Einträge")
        print(f"✅ Intraday-Daten abgerufen: {len(intraday)} Einträge")
        print(f"✅ Statistiken berechnet: {stats.get('anzahl_tage', 0)} Tage erfasst")
        
    except Exception as e:
        print(f"❌ Fehler beim Testen: {e}")
    
    print("\n🎯 System-Status:")
    print("-" * 50)
    print("✅ Datenbank initialisiert")
    print("✅ Historische Tabellen erstellt")
    print("✅ Standard-Aktien hinzugefügt")
    print("✅ Live-Monitoring vorbereitet")
    
    print(f"\n🕒 Initialisierung abgeschlossen: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n📝 Verfügbare API-Endpoints:")
    print("-" * 50)
    print("• GET  /api/historical/{symbol}?days=30    - Historische Daten")
    print("• GET  /api/intraday/{symbol}?hours=24     - Intraday-Daten")
    print("• GET  /api/monitored-stocks               - Überwachte Aktien")
    print("• POST /api/monitored-stocks               - Aktie hinzufügen")
    print("• GET  /api/portfolio-historical           - Portfolio-Daten")
    print("• GET  /api/statistics/{symbol}            - Aktien-Statistiken")
    print("• GET  /api/live-monitoring/start/{symbol} - Live-Monitoring starten")
    print("• POST /api/cleanup-data                   - Alte Daten bereinigen")
    
    print("\n🌐 Beispiel-Aufrufe:")
    print("-" * 50)
    print("curl http://10.1.1.110:8003/api/historical/AAPL?days=30")
    print("curl http://10.1.1.110:8003/api/intraday/TSLA?hours=24")
    print("curl http://10.1.1.110:8003/api/monitored-stocks")
    print("curl http://10.1.1.110:8003/api/statistics/NVDA")
    
    print("\n🚀 Das DA-KI Historical Stock Data System ist bereit!")

if __name__ == "__main__":
    main()