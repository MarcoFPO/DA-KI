#!/usr/bin/env python3
"""
Historical Stock Data Service für DA-KI
Speichert Live-Monitoring Daten mit zeitlichem Verlauf
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests

class HistoricalStockDataManager:
    def __init__(self, db_path: str = "/home/mdoehler/data-web-app/database/aktienanalyse_de.db"):
        self.db_path = db_path
        self.init_historical_tables()
    
    def init_historical_tables(self):
        """Initialisiert die Tabellen für historische Aktiendaten"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabelle für tägliche historische Kursdaten
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historical_stock_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                datum DATE NOT NULL,
                open_price REAL,
                high_price REAL,
                low_price REAL,
                close_price REAL,
                volume INTEGER,
                market_cap TEXT,
                pe_ratio TEXT,
                change_amount REAL,
                change_percent TEXT,
                erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, datum)
            )
        """)
        
        # Tabelle für Intraday-Daten (5-Minuten-Intervalle)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS intraday_stock_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                price REAL NOT NULL,
                volume INTEGER,
                change_amount REAL,
                change_percent TEXT,
                erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timestamp)
            )
        """)
        
        # Tabelle für Aktienliste mit Live-Monitoring Status
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitored_stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                monitoring_interval INTEGER DEFAULT 300,
                letztes_update TIMESTAMP,
                erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Index für Performance-Optimierung
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_historical_symbol_datum ON historical_stock_data(symbol, datum)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_intraday_symbol_timestamp ON intraday_stock_data(symbol, timestamp)")
        
        conn.commit()
        conn.close()
    
    def add_monitored_stock(self, symbol: str, name: str, monitoring_interval: int = 300):
        """Fügt eine Aktie zur Live-Monitoring Liste hinzu"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO monitored_stocks (symbol, name, monitoring_interval)
            VALUES (?, ?, ?)
        """, (symbol.upper(), name, monitoring_interval))
        
        conn.commit()
        conn.close()
    
    def get_monitored_stocks(self) -> List[Dict[str, Any]]:
        """Holt die Liste der überwachten Aktien"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, name, is_active, monitoring_interval, letztes_update
            FROM monitored_stocks 
            WHERE is_active = 1
            ORDER BY symbol
        """)
        
        stocks = []
        for row in cursor.fetchall():
            stocks.append({
                'symbol': row[0],
                'name': row[1],
                'is_active': bool(row[2]),
                'monitoring_interval': row[3],
                'letztes_update': row[4]
            })
        
        conn.close()
        return stocks
    
    def save_historical_data(self, symbol: str, stock_data: Dict[str, Any], datum: str = None):
        """Speichert tägliche historische Daten"""
        if datum is None:
            datum = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Extrahiere Preisdaten
        current_price = stock_data.get('current_price', 0)
        change_str = stock_data.get('change', '0')
        change_amount = float(change_str.replace('+', '').replace(',', '.')) if change_str else 0
        
        cursor.execute("""
            INSERT OR REPLACE INTO historical_stock_data 
            (symbol, datum, close_price, market_cap, pe_ratio, change_amount, change_percent)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            symbol.upper(),
            datum,
            current_price,
            stock_data.get('market_cap', ''),
            stock_data.get('pe_ratio', ''),
            change_amount,
            stock_data.get('change_percent', '')
        ))
        
        # Update letztes_update in monitored_stocks
        cursor.execute("""
            UPDATE monitored_stocks 
            SET letztes_update = CURRENT_TIMESTAMP 
            WHERE symbol = ?
        """, (symbol.upper(),))
        
        conn.commit()
        conn.close()
    
    def save_intraday_data(self, symbol: str, price: float, volume: int = None, 
                          change_amount: float = None, change_percent: str = None):
        """Speichert Intraday-Daten (5-Minuten-Intervalle)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Runde auf 5-Minuten-Intervall
        now = datetime.now()
        rounded_minutes = (now.minute // 5) * 5
        timestamp = now.replace(minute=rounded_minutes, second=0, microsecond=0)
        
        cursor.execute("""
            INSERT OR REPLACE INTO intraday_stock_data 
            (symbol, timestamp, price, volume, change_amount, change_percent)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            symbol.upper(),
            timestamp,
            price,
            volume,
            change_amount,
            change_percent
        ))
        
        conn.commit()
        conn.close()
    
    def get_historical_data(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """Holt historische Daten für eine Aktie"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT datum, open_price, high_price, low_price, close_price, 
                   volume, market_cap, pe_ratio, change_amount, change_percent
            FROM historical_stock_data 
            WHERE symbol = ? AND datum >= ?
            ORDER BY datum DESC
        """, (symbol.upper(), start_date))
        
        data = []
        for row in cursor.fetchall():
            data.append({
                'datum': row[0],
                'open_price': row[1],
                'high_price': row[2],
                'low_price': row[3],
                'close_price': row[4],
                'volume': row[5],
                'market_cap': row[6],
                'pe_ratio': row[7],
                'change_amount': row[8],
                'change_percent': row[9]
            })
        
        conn.close()
        return data
    
    def get_intraday_data(self, symbol: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Holt Intraday-Daten für eine Aktie"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_time = datetime.now() - timedelta(hours=hours)
        
        cursor.execute("""
            SELECT timestamp, price, volume, change_amount, change_percent
            FROM intraday_stock_data 
            WHERE symbol = ? AND timestamp >= ?
            ORDER BY timestamp DESC
        """, (symbol.upper(), start_time))
        
        data = []
        for row in cursor.fetchall():
            data.append({
                'timestamp': row[0],
                'price': row[1],
                'volume': row[2],
                'change_amount': row[3],
                'change_percent': row[4]
            })
        
        conn.close()
        return data
    
    def get_portfolio_historical_data(self, symbols: List[str], days: int = 30) -> Dict[str, List[Dict[str, Any]]]:
        """Holt historische Daten für ein Portfolio von Aktien"""
        portfolio_data = {}
        for symbol in symbols:
            portfolio_data[symbol] = self.get_historical_data(symbol, days)
        return portfolio_data
    
    def cleanup_old_data(self, keep_days: int = 90, keep_intraday_days: int = 7):
        """Bereinigt alte Daten um Speicherplatz zu sparen"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Lösche alte tägliche Daten
        cutoff_date = (datetime.now() - timedelta(days=keep_days)).strftime('%Y-%m-%d')
        cursor.execute("DELETE FROM historical_stock_data WHERE datum < ?", (cutoff_date,))
        
        # Lösche alte Intraday-Daten
        cutoff_timestamp = datetime.now() - timedelta(days=keep_intraday_days)
        cursor.execute("DELETE FROM intraday_stock_data WHERE timestamp < ?", (cutoff_timestamp,))
        
        conn.commit()
        conn.close()
    
    def get_stock_statistics(self, symbol: str) -> Dict[str, Any]:
        """Berechnet Statistiken für eine Aktie"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Grundlegende Statistiken
        cursor.execute("""
            SELECT 
                COUNT(*) as anzahl_tage,
                MIN(close_price) as min_preis,
                MAX(close_price) as max_preis,
                AVG(close_price) as avg_preis,
                MIN(datum) as erste_aufzeichnung,
                MAX(datum) as letzte_aufzeichnung
            FROM historical_stock_data 
            WHERE symbol = ?
        """, (symbol.upper(),))
        
        stats = cursor.fetchone()
        
        if stats and stats[0] > 0:
            result = {
                'symbol': symbol.upper(),
                'anzahl_tage': stats[0],
                'min_preis': stats[1],
                'max_preis': stats[2],
                'avg_preis': round(stats[3], 2) if stats[3] else 0,
                'erste_aufzeichnung': stats[4],
                'letzte_aufzeichnung': stats[5]
            }
            
            # Berechne Volatilität (einfache Standardabweichung)
            cursor.execute("""
                SELECT close_price FROM historical_stock_data 
                WHERE symbol = ? ORDER BY datum
            """, (symbol.upper(),))
            
            prices = [row[0] for row in cursor.fetchall() if row[0]]
            if len(prices) > 1:
                import statistics
                result['volatilität'] = round(statistics.stdev(prices), 2)
                
                # Berechne 30-Tage-Trend
                if len(prices) >= 30:
                    recent_avg = sum(prices[-30:]) / 30
                    older_avg = sum(prices[-60:-30]) / 30 if len(prices) >= 60 else result['avg_preis']
                    result['30_tage_trend'] = round(((recent_avg - older_avg) / older_avg) * 100, 2)
        else:
            result = {
                'symbol': symbol.upper(),
                'anzahl_tage': 0,
                'message': 'Keine historischen Daten verfügbar'
            }
        
        conn.close()
        return result