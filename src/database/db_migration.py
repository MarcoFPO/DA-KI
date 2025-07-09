#!/usr/bin/env python3
"""
Database Schema Migration für DA-KI
Vereinheitlicht Legacy und neue API Schemas
"""

import sqlite3
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseMigration:
    """Database Migration Manager"""
    
    def __init__(self, db_path: str = "./data/daki.db"):
        self.db_path = db_path
        self.backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def backup_database(self):
        """Erstelle Backup der aktuellen Datenbank"""
        if os.path.exists(self.db_path):
            import shutil
            shutil.copy2(self.db_path, self.backup_path)
            logger.info(f"✅ Backup erstellt: {self.backup_path}")
        
    def check_existing_schema(self):
        """Prüfe existierendes Schema"""
        if not os.path.exists(self.db_path):
            logger.info("📋 Neue Datenbank - kein Migration nötig")
            return {"legacy": False, "new_api": False}
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Prüfe auf Legacy-Tabellen
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        status = {
            "legacy": "candidates" in tables or "historical_data" in tables,
            "new_api": "users" in tables or "portfolios" in tables,
            "tables": tables
        }
        
        conn.close()
        return status
    
    def migrate_to_unified_schema(self):
        """Migriere zu einheitlichem Schema"""
        print("🔄 Starte Database Migration...")
        
        # 1. Backup erstellen
        self.backup_database()
        
        # 2. Schema-Status prüfen
        status = self.check_existing_schema()
        print(f"📊 Aktueller Status: {status}")
        
        # 3. Erstelle neues einheitliches Schema
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Neue einheitliche Tabellen
        self._create_unified_tables(cursor)
        
        # 4. Migriere Legacy-Daten falls vorhanden
        if status["legacy"]:
            self._migrate_legacy_data(cursor)
            
        # 5. Migration abschließen
        cursor.execute("PRAGMA user_version = 2")  # Schema Version
        conn.commit()
        conn.close()
        
        print("✅ Database Migration abgeschlossen")
        
    def _create_unified_tables(self, cursor):
        """Erstelle einheitliche Tabellen-Struktur"""
        
        # Users Tabelle (für neue API)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                password_hash TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Portfolios Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL DEFAULT 'Default Portfolio',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Stocks Tabelle (vereinheitlicht candidates + neue Felder)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                company_name TEXT,
                quantity INTEGER NOT NULL DEFAULT 0,
                average_buy_price REAL,
                current_price REAL,
                total_cost REAL,
                current_value REAL,
                selection_reason TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (portfolio_id) REFERENCES portfolios (id)
            )
        ''')
        
        # Historical Data (erweitert für neue API)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_historical_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL, high REAL, low REAL, close REAL,
                volume INTEGER,
                rsi REAL, macd REAL, macd_signal REAL, macd_hist REAL,
                ema10 REAL, ema20 REAL, ema50 REAL,
                bollinger_upper REAL, bollinger_middle REAL, bollinger_lower REAL,
                atr REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ticker, date)
            )
        ''')
        
        # Analysis Results (für KI-Predictions)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                analysis_type TEXT NOT NULL,
                growth_score REAL,
                confidence_level REAL,
                predicted_price REAL,
                prediction_period_days INTEGER,
                model_version TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        logger.info("✅ Einheitliche Tabellen erstellt")
        
    def _migrate_legacy_data(self, cursor):
        """Migriere Legacy-Daten zur neuen Struktur"""
        logger.info("🔄 Migriere Legacy-Daten...")
        
        # Erstelle Default-User für Legacy-Daten
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password_hash, is_admin)
            VALUES ('legacy_user', 'legacy_hash', 0)
        ''')
        
        # Erstelle Default-Portfolio
        cursor.execute('''
            INSERT OR IGNORE INTO portfolios (user_id, name)
            SELECT id, 'Legacy Portfolio' FROM users WHERE username = 'legacy_user'
        ''')
        
        # Migriere candidates -> stocks
        try:
            cursor.execute('''
                INSERT INTO stocks (portfolio_id, ticker, selection_reason, added_at)
                SELECT p.id, c.ticker, c.selection_reason, c.timestamp
                FROM candidates c
                CROSS JOIN portfolios p
                WHERE p.name = 'Legacy Portfolio'
            ''')
            logger.info("✅ Legacy candidates migriert")
        except sqlite3.Error as e:
            logger.warning(f"⚠️ Candidates Migration: {e}")
        
        # Migriere historical_data -> stock_historical_data
        try:
            cursor.execute('''
                INSERT INTO stock_historical_data 
                SELECT * FROM historical_data WHERE 1=1
            ''')
            logger.info("✅ Legacy historical_data migriert")
        except sqlite3.Error as e:
            logger.warning(f"⚠️ Historical Data Migration: {e}")


def main():
    """Hauptfunktion für Migration"""
    print("🗄️ DA-KI Database Migration Tool")
    print("=" * 40)
    
    migration = DatabaseMigration()
    
    # Status prüfen
    status = migration.check_existing_schema()
    print(f"📊 Aktueller DB-Status: {status}")
    
    if not status["legacy"] and not status["new_api"]:
        print("📋 Neue Installation - erstelle frisches Schema")
        migration._create_unified_tables(sqlite3.connect(migration.db_path).cursor())
    else:
        print("🔄 Migration erforderlich")
        migration.migrate_to_unified_schema()
    
    print("✅ Migration abgeschlossen!")

if __name__ == "__main__":
    main()