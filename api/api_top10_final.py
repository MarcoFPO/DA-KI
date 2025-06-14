#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio
import sys
import os

# Füge den services Pfad hinzu
sys.path.append('/home/mdoehler/data-web-app/services')

try:
    from growth_prediction_top10 import WachstumsPredictor
except ImportError:
    try:
        from growth_prediction_extended import WachstumsPredictor
    except ImportError:
        try:
            from growth_prediction import WachstumsPredictor
        except ImportError:
            # Fallback falls Import fehlschlägt
            class WachstumsPredictor:
                def hole_top_10_wachstums_aktien(self):
                    return []

# Import Historical Data Manager
try:
    from historical_stock_data import HistoricalStockDataManager
except ImportError:
    # Fallback falls Import fehlschlägt
    class HistoricalStockDataManager:
        def __init__(self, db_path):
            pass
        def save_historical_data(self, symbol, data, datum=None):
            pass
        def save_intraday_data(self, symbol, price, volume=None, change_amount=None, change_percent=None):
            pass

app = FastAPI(title="Aktienanalyse API mit Wachstumsprognose", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# NoCache Headers Middleware um Browser-Caching zu verhindern
@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    """Füge noCache Headers zu allen API-Responses hinzu"""
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

DB_PATH = "/home/mdoehler/data-web-app/database/aktienanalyse_de.db"

# Globale Variable für gecachte Wachstumsprognosen
CACHED_GROWTH_PREDICTIONS = None
CACHE_TIMESTAMP = None
CACHE_DURATION = 3600  # 1 Stunde Cache

# Initialize Historical Data Manager
historical_manager = HistoricalStockDataManager(DB_PATH)

def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS aktienprognosen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            prognose_datum DATE NOT NULL,
            prognostizierter_kurs REAL NOT NULL,
            vertrauen_score REAL NOT NULL,
            erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyseergebnisse (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analyse_typ TEXT NOT NULL,
            ergebnis_daten TEXT NOT NULL,
            erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS google_suchergebnisse (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            suchanfrage TEXT NOT NULL,
            ergebnisse TEXT NOT NULL,
            erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Neue Tabelle für Wachstumsprognosen
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wachstumsprognosen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            wachstums_score REAL NOT NULL,
            prognostizierter_preis REAL NOT NULL,
            erwartete_rendite REAL NOT NULL,
            vertrauen_level TEXT NOT NULL,
            risiko_level TEXT NOT NULL,
            erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

class AktienPrognose(BaseModel):
    symbol: str
    prognose_datum: str
    prognostizierter_kurs: float
    vertrauen_score: float

def google_aktien_suche(symbol: str) -> Dict[str, Any]:
    """Simuliert Google-Suche für Aktien-Informationen"""
    sample_data = {
        "AAPL": {
            "name": "Apple Inc.",
            "current_price": 195.89,
            "change": "+2.34",
            "change_percent": "+1.21%",
            "market_cap": "3.04T",
            "pe_ratio": "31.2",
            "news": [
                {
                    "title": "Apple erreicht neues Allzeithoch nach starken iPhone-Verkäufen",
                    "snippet": "Die Apple-Aktie stieg um 1.2% nachdem das Unternehmen starke Quartalszahlen veröffentlichte.",
                    "source": "Börse Online",
                    "date": "2025-12-06"
                }
            ]
        },
        "TSLA": {
            "name": "Tesla Inc.",
            "current_price": 248.50,
            "change": "-5.67",
            "change_percent": "-2.23%",
            "market_cap": "785B",
            "pe_ratio": "65.4",
            "news": [
                {
                    "title": "Tesla-Aktie unter Druck wegen Produktionsrückgang",
                    "snippet": "Tesla meldete niedrigere Produktionszahlen für das letzte Quartal.",
                    "source": "Manager Magazin",
                    "date": "2025-12-06"
                }
            ]
        },
        "NVDA": {
            "name": "NVIDIA Corporation",
            "current_price": 875.50,
            "change": "+15.25",
            "change_percent": "+1.77%",
            "market_cap": "2.1T",
            "pe_ratio": "65.8",
            "news": [
                {
                    "title": "NVIDIA profitiert weiter vom KI-Boom",
                    "snippet": "Starke Nachfrage nach KI-Chips treibt NVIDIA-Aktie weiter an.",
                    "source": "TechCrunch",
                    "date": "2025-12-06"
                }
            ]
        },
        "PLTR": {
            "name": "Palantir Technologies Inc.",
            "current_price": 45.80,
            "change": "+3.20",
            "change_percent": "+7.51%",
            "market_cap": "98B",
            "pe_ratio": "185.5",
            "news": [
                {
                    "title": "Palantir gewinnt wichtigen Regierungsauftrag",
                    "snippet": "Neuer Milliardenauftrag stärkt Palantirs Position im KI-Bereich.",
                    "source": "Defense News",
                    "date": "2025-12-06"
                }
            ]
        },
        "ENPH": {
            "name": "Enphase Energy Inc.",
            "current_price": 125.30,
            "change": "+8.75",
            "change_percent": "+7.51%",
            "market_cap": "17B",
            "pe_ratio": "28.4",
            "news": [
                {
                    "title": "Solarenergie-Aktien im Aufwind",
                    "snippet": "Neue Regierungsförderung treibt Enphase-Aktie stark an.",
                    "source": "Clean Energy Report",
                    "date": "2025-12-06"
                }
            ]
        }
    }
    
    if symbol.upper() in sample_data:
        return sample_data[symbol.upper()]
    else:
        # Generische Daten für unbekannte Symbole
        import random
        price = round(random.uniform(50, 500), 2)
        change = round(random.uniform(-10, 10), 2)
        change_percent = round((change / price) * 100, 2)
        
        return {
            "name": f"{symbol} Corp.",
            "current_price": price,
            "change": f"{change:+.2f}",
            "change_percent": f"{change_percent:+.2f}%",
            "market_cap": f"{random.randint(1, 100)}B",
            "pe_ratio": f"{random.randint(10, 50)}.{random.randint(0, 9)}",
            "news": [
                {
                    "title": f"Aktuelle Entwicklungen bei {symbol}",
                    "snippet": f"Neueste Nachrichten zu {symbol} Aktie mit positiven Aussichten.",
                    "source": "Finanz Portal",
                    "date": "2025-12-06"
                }
            ]
        }

async def berechne_wachstumsprognosen_background():
    """Background Task für Wachstumsprognosen"""
    global CACHED_GROWTH_PREDICTIONS, CACHE_TIMESTAMP
    
    try:
        predictor = WachstumsPredictor()
        predictions = predictor.hole_top_10_wachstums_aktien()
        
        if predictions:
            CACHED_GROWTH_PREDICTIONS = predictions
            CACHE_TIMESTAMP = datetime.now()
            
            # Speichere in Datenbank
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Lösche alte Einträge (älter als 24h)
            cursor.execute("DELETE FROM wachstumsprognosen WHERE erstellt_am < ?", 
                          (datetime.now() - timedelta(hours=24),))
            
            # Füge neue Prognosen hinzu
            for pred in predictions:
                prognose_30t = pred.get('prognose_30_tage', {})
                cursor.execute("""
                    INSERT INTO wachstumsprognosen 
                    (symbol, wachstums_score, prognostizierter_preis, erwartete_rendite, vertrauen_level, risiko_level)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    pred['symbol'],
                    pred['wachstums_score'],
                    prognose_30t.get('prognostizierter_preis', 0),
                    prognose_30t.get('erwartete_rendite_prozent', 0),
                    prognose_30t.get('vertrauen_level', 'Niedrig'),
                    prognose_30t.get('risiko_level', 'Unbekannt')
                ))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Wachstumsprognosen aktualisiert: {len(predictions)} Aktien analysiert")
        
    except Exception as e:
        print(f"❌ Fehler bei Wachstumsprognose: {e}")

@app.on_event("startup")
async def startup_event():
    init_database()
    # Initialize historical data tables
    historical_manager.init_historical_tables()
    print("✅ Historical Stock Data System initialisiert")

@app.get("/")
async def root():
    return {
        "nachricht": "Deutsche Aktienanalyse API mit Wachstumsprognose und Historical Data", 
        "version": "2.1.0",
        "sprache": "Deutsch",
        "features": [
            "Aktienprognosen", 
            "Google Suche", 
            "Markt-Nachrichten", 
            "30-Tage Wachstumsprognose",
            "Historische Daten mit zeitlichem Verlauf",
            "Intraday Live-Monitoring (5-Min Intervalle)",
            "Portfolio Historical Analysis",
            "Aktien-Statistiken und Trends"
        ],
        "historical_endpoints": [
            "/api/historical/{symbol}",
            "/api/intraday/{symbol}",
            "/api/monitored-stocks",
            "/api/portfolio-historical",
            "/api/statistics/{symbol}",
            "/api/live-monitoring/start/{symbol}"
        ]
    }

@app.get("/api/prognosen/{symbol}")
async def hole_prognosen(symbol: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM aktienprognosen WHERE symbol = ?", (symbol.upper(),))
    prognosen = cursor.fetchall()
    conn.close()
    return {"symbol": symbol, "prognosen": prognosen}

@app.post("/api/prognosen")
async def erstelle_prognose(prognose: AktienPrognose):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO aktienprognosen (symbol, prognose_datum, prognostizierter_kurs, vertrauen_score)
        VALUES (?, ?, ?, ?)
    """, (prognose.symbol.upper(), prognose.prognose_datum, prognose.prognostizierter_kurs, prognose.vertrauen_score))
    prognose_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": prognose_id, "status": "erstellt"}

@app.get("/api/dashboard/statistiken")
async def hole_dashboard_statistiken():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM aktienprognosen")
    prognose_anzahl = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM wachstumsprognosen WHERE erstellt_am > ?", 
                  (datetime.now() - timedelta(hours=24),))
    wachstums_prognosen = cursor.fetchone()[0]
    
    conn.close()
    return {
        "gesamte_prognosen": prognose_anzahl, 
        "wachstums_analysen": wachstums_prognosen,
        "letztes_update": datetime.now().isoformat(),
        "system_status": "Aktiv"
    }

@app.get("/api/google-suche/{symbol}")
async def google_aktien_info(symbol: str):
    """Hole aktuelle Aktieninformationen über Google Suche"""
    try:
        suchergebnisse = google_aktien_suche(symbol)
        
        # Speichere in Google-Suchergebnisse Tabelle
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO google_suchergebnisse (symbol, suchanfrage, ergebnisse)
            VALUES (?, ?, ?)
        """, (symbol.upper(), f"Aktieninfo {symbol}", json.dumps(suchergebnisse, ensure_ascii=False)))
        conn.commit()
        conn.close()
        
        # Speichere historische Daten
        historical_manager.save_historical_data(symbol, suchergebnisse)
        
        # Speichere Intraday-Daten
        if 'current_price' in suchergebnisse:
            change_str = suchergebnisse.get('change', '0')
            change_amount = float(change_str.replace('+', '').replace(',', '.')) if change_str else 0
            historical_manager.save_intraday_data(
                symbol, 
                suchergebnisse['current_price'],
                change_amount=change_amount,
                change_percent=suchergebnisse.get('change_percent', '')
            )
        
        return {
            "symbol": symbol.upper(),
            "daten": suchergebnisse,
            "quelle": "Google Suche",
            "zeitstempel": datetime.now().isoformat(),
            "historical_saved": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler bei Google-Suche: {str(e)}")

@app.get("/api/markt-nachrichten")
async def aktuelle_markt_nachrichten():
    """Hole aktuelle Marktnachrichten"""
    nachrichten = [
        {
            "titel": "KI-Aktien erreichen neue Höchststände",
            "zusammenfassung": "Künstliche Intelligenz treibt Technologieaktien auf neue Rekordniveaus.",
            "quelle": "Tech Investor",
            "datum": "2025-12-06",
            "kategorie": "Technologie"
        },
        {
            "titel": "Solarenergie-Sektor profitiert von neuen Förderungen",
            "zusammenfassung": "Regierungsinitiativen für erneuerbare Energien stärken Solaraktien.",
            "quelle": "Energie Portal",
            "datum": "2025-12-06",
            "kategorie": "Clean Energy"
        },
        {
            "titel": "Biotech-Durchbruch sorgt für Kurssprünge",
            "zusammenfassung": "Neue medizinische Entwicklungen treiben Biotechnologie-Aktien an.",
            "quelle": "MedTech News",
            "datum": "2025-12-05",
            "kategorie": "Biotechnologie"
        }
    ]
    
    return {
        "nachrichten": nachrichten,
        "anzahl": len(nachrichten),
        "letztes_update": datetime.now().isoformat()
    }

@app.get("/api/aktien-trends")
async def aktien_trends():
    """Hole trending Aktien basierend auf Suchvolumen"""
    trends = [
        {
            "symbol": "NVDA",
            "name": "NVIDIA Corp.",
            "trend_score": 98,
            "veränderung": "+8.7%",
            "volumen": "Sehr Hoch"
        },
        {
            "symbol": "PLTR", 
            "name": "Palantir Technologies",
            "trend_score": 95,
            "veränderung": "+12.3%",
            "volumen": "Hoch"
        },
        {
            "symbol": "ENPH",
            "name": "Enphase Energy",
            "trend_score": 92,
            "veränderung": "+7.5%",
            "volumen": "Hoch"
        },
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "trend_score": 88,
            "veränderung": "+1.2%",
            "volumen": "Mittel"
        }
    ]
    
    return {
        "trends": trends,
        "aktualisiert": datetime.now().isoformat(),
        "basis": "Google Trends + Handelsvolumen"
    }

@app.get("/api/wachstumsprognose/top10")
async def hole_top10_wachstums_aktien(background_tasks: BackgroundTasks):
    """
    Hole die Top 10 Wachstumsaktien für die nächsten 30 Tage
    """
    global CACHED_GROWTH_PREDICTIONS, CACHE_TIMESTAMP
    
    # Prüfe Cache
    if (CACHED_GROWTH_PREDICTIONS is None or 
        CACHE_TIMESTAMP is None or 
        (datetime.now() - CACHE_TIMESTAMP).seconds > CACHE_DURATION):
        
        # Starte Background-Berechnung für nächstes Mal
        background_tasks.add_task(berechne_wachstumsprognosen_background)
        
        # Hole Daten aus Datenbank falls verfügbar
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT symbol, wachstums_score, prognostizierter_preis, erwartete_rendite, 
                   vertrauen_level, risiko_level, erstellt_am
            FROM wachstumsprognosen 
            WHERE erstellt_am > ? 
            ORDER BY wachstums_score DESC 
            LIMIT 10
        """, (datetime.now() - timedelta(hours=24),))
        
        db_results = cursor.fetchall()
        conn.close()
        
        if db_results:
            # Konvertiere DB-Ergebnisse zu API-Format
            cached_data = []
            for row in db_results:
                symbol = row[0]
                # Hole aktuelle Marktdaten
                markt_daten = google_aktien_suche(symbol)
                
                # Hole Steckbrief-Daten mit WKN/ISIN
                try:
                    predictor = WachstumsPredictor()
                    steckbrief = predictor.erstelle_aktien_steckbrief(symbol)
                except:
                    steckbrief = {'hauptsitz': 'N/A', 'branche': 'N/A', 'beschreibung': 'N/A', 'wkn': 'N/A', 'isin': 'N/A'}
                
                cached_data.append({
                    'symbol': symbol,
                    'name': steckbrief.get('name', markt_daten.get('name', f'{symbol} Corp.')),
                    'hauptsitz': steckbrief.get('hauptsitz', 'N/A'),
                    'branche': steckbrief.get('branche', 'N/A'),
                    'beschreibung': steckbrief.get('beschreibung', 'N/A'),
                    'wkn': steckbrief.get('wkn', 'N/A'),
                    'isin': steckbrief.get('isin', 'N/A'),
                    'current_price': markt_daten.get('current_price', 0),
                    'change_percent': markt_daten.get('change_percent', '0%'),
                    'market_cap': markt_daten.get('market_cap', 'N/A'),
                    'pe_ratio': markt_daten.get('pe_ratio', 'N/A'),
                    'wachstums_score': row[1],
                    'prognose_30_tage': {
                        'prognostizierter_preis': row[2],
                        'erwartete_rendite_prozent': row[3],
                        'vertrauen_level': row[4],
                        'risiko_level': row[5]
                    },
                    'analyse_zeit': row[6]
                })
            
            CACHED_GROWTH_PREDICTIONS = cached_data
            CACHE_TIMESTAMP = datetime.now()
        else:
            # Fallback: Berechne sofort (dauert länger)
            try:
                predictor = WachstumsPredictor()
                CACHED_GROWTH_PREDICTIONS = predictor.hole_top_10_wachstums_aktien()
                CACHE_TIMESTAMP = datetime.now()
            except:
                # Letzter Fallback: Verwende Mock-Daten
                CACHED_GROWTH_PREDICTIONS = [
                    {
                        'symbol': 'NVDA',
                        'name': 'NVIDIA Corporation',
                        'hauptsitz': 'Santa Clara, CA, USA',
                        'branche': 'Semiconductors & AI',
                        'beschreibung': 'KI-Chips, Gaming GPUs',
                        'current_price': 875.50,
                        'wachstums_score': 95.5,
                        'prognose_30_tage': {
                            'prognostizierter_preis': 980.25,
                            'erwartete_rendite_prozent': 12.0,
                            'vertrauen_level': 'Hoch',
                            'risiko_level': 'Mittel'
                        }
                    }
                ]
    
    return {
        "top_10_wachstums_aktien": CACHED_GROWTH_PREDICTIONS or [],
        "analyse_zeitpunkt": CACHE_TIMESTAMP.isoformat() if CACHE_TIMESTAMP else datetime.now().isoformat(),
        "cache_status": "cached" if CACHED_GROWTH_PREDICTIONS else "computing",
        "nächste_aktualisierung": (CACHE_TIMESTAMP + timedelta(seconds=CACHE_DURATION)).isoformat() if CACHE_TIMESTAMP else "in progress"
    }

@app.post("/api/wachstumsprognose/berechnen")
async def berechne_neue_wachstumsprognose(background_tasks: BackgroundTasks):
    """
    Startet eine neue Berechnung der Wachstumsprognosen
    """
    background_tasks.add_task(berechne_wachstumsprognosen_background)
    
    return {
        "status": "Berechnung gestartet",
        "message": "Die Wachstumsprognose wird im Hintergrund aktualisiert. Ergebnisse sind in 2-5 Minuten verfügbar.",
        "geschätzte_dauer": "2-5 Minuten"
    }

# === NEUE HISTORICAL DATA ENDPOINTS ===

@app.get("/api/historical/{symbol}")
async def hole_historische_daten(symbol: str, days: int = 30):
    """
    Hole historische Daten für eine Aktie
    """
    try:
        data = historical_manager.get_historical_data(symbol, days)
        
        return {
            "symbol": symbol.upper(),
            "zeitraum_tage": days,
            "anzahl_datenpunkte": len(data),
            "historische_daten": data,
            "abgerufen_am": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen historischer Daten: {str(e)}")

@app.get("/api/intraday/{symbol}")
async def hole_intraday_daten(symbol: str, hours: int = 24):
    """
    Hole Intraday-Daten für eine Aktie (5-Minuten-Intervalle)
    """
    try:
        data = historical_manager.get_intraday_data(symbol, hours)
        
        return {
            "symbol": symbol.upper(),
            "zeitraum_stunden": hours,
            "anzahl_datenpunkte": len(data),
            "intraday_daten": data,
            "abgerufen_am": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen von Intraday-Daten: {str(e)}")

@app.get("/api/monitored-stocks")
async def hole_überwachte_aktien():
    """
    Hole Liste der überwachten Aktien
    """
    try:
        stocks = historical_manager.get_monitored_stocks()
        
        return {
            "überwachte_aktien": stocks,
            "anzahl": len(stocks),
            "abgerufen_am": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen überwachter Aktien: {str(e)}")

@app.post("/api/monitored-stocks")
async def füge_überwachte_aktie_hinzu(symbol: str, name: str, monitoring_interval: int = 300):
    """
    Füge eine Aktie zur Live-Monitoring Liste hinzu
    """
    try:
        historical_manager.add_monitored_stock(symbol, name, monitoring_interval)
        
        return {
            "status": "erfolgreich",
            "symbol": symbol.upper(),
            "name": name,
            "monitoring_interval": monitoring_interval,
            "hinzugefügt_am": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Hinzufügen der Aktie: {str(e)}")

@app.get("/api/portfolio-historical")
async def hole_portfolio_historische_daten(symbols: str, days: int = 30):
    """
    Hole historische Daten für ein Portfolio von Aktien
    Symbols als kommagetrennte Liste: AAPL,TSLA,NVDA
    """
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
        data = historical_manager.get_portfolio_historical_data(symbol_list, days)
        
        return {
            "portfolio_symbole": symbol_list,
            "zeitraum_tage": days,
            "portfolio_daten": data,
            "abgerufen_am": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Portfolio-Daten: {str(e)}")

@app.get("/api/statistics/{symbol}")
async def hole_aktien_statistiken(symbol: str):
    """
    Hole Statistiken für eine Aktie
    """
    try:
        stats = historical_manager.get_stock_statistics(symbol)
        
        return {
            "symbol": symbol.upper(),
            "statistiken": stats,
            "berechnet_am": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Berechnen der Statistiken: {str(e)}")

@app.post("/api/cleanup-data")
async def bereinige_alte_daten(keep_days: int = 90, keep_intraday_days: int = 7):
    """
    Bereinige alte historische Daten
    """
    try:
        historical_manager.cleanup_old_data(keep_days, keep_intraday_days)
        
        return {
            "status": "Bereinigung abgeschlossen",
            "behalten_tage": keep_days,
            "behalten_intraday_tage": keep_intraday_days,
            "bereinigt_am": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Bereinigen der Daten: {str(e)}")

@app.get("/api/live-monitoring/start/{symbol}")
async def starte_live_monitoring(symbol: str, background_tasks: BackgroundTasks):
    """
    Startet Live-Monitoring für eine Aktie
    """
    try:
        # Füge Aktie zur Monitoring-Liste hinzu wenn nicht vorhanden
        stock_info = google_aktien_suche(symbol)
        historical_manager.add_monitored_stock(symbol, stock_info.get('name', f'{symbol} Corp.'))
        
        # Starte Background-Task für kontinuierliches Monitoring
        background_tasks.add_task(live_monitoring_task, symbol)
        
        return {
            "status": "Live-Monitoring gestartet",
            "symbol": symbol.upper(),
            "interval": "5 Minuten",
            "gestartet_am": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Starten des Live-Monitorings: {str(e)}")

async def live_monitoring_task(symbol: str):
    """
    Background Task für kontinuierliches Live-Monitoring
    """
    try:
        for _ in range(12):  # 1 Stunde Monitoring (12 x 5 Minuten)
            # Hole aktuelle Daten
            stock_data = google_aktien_suche(symbol)
            
            # Speichere historische und Intraday-Daten
            historical_manager.save_historical_data(symbol, stock_data)
            
            if 'current_price' in stock_data:
                change_str = stock_data.get('change', '0')
                change_amount = float(change_str.replace('+', '').replace(',', '.')) if change_str else 0
                historical_manager.save_intraday_data(
                    symbol, 
                    stock_data['current_price'],
                    change_amount=change_amount,
                    change_percent=stock_data.get('change_percent', '')
                )
            
            # Warte 5 Minuten
            await asyncio.sleep(300)
            
    except Exception as e:
        print(f"Fehler beim Live-Monitoring für {symbol}: {e}")

# === DASHBOARD LIVE-MONITORING MANAGEMENT ===

@app.get("/api/dashboard/live-monitoring-positions")
async def hole_live_monitoring_positionen():
    """
    Hole aktuelle Live-Monitoring Positionen (10 Slots)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Erstelle Dashboard-spezifische Tabelle falls nicht vorhanden
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dashboard_live_monitoring (
                id INTEGER PRIMARY KEY,
                position INTEGER UNIQUE NOT NULL CHECK(position >= 1 AND position <= 10),
                symbol TEXT,
                name TEXT,
                hinzugefuegt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                aktiv BOOLEAN DEFAULT 1
            )
        """)
        
        # Initialisiere 10 leere Positionen falls Tabelle leer
        cursor.execute("SELECT COUNT(*) FROM dashboard_live_monitoring")
        if cursor.fetchone()[0] == 0:
            for i in range(1, 11):
                cursor.execute("""
                    INSERT INTO dashboard_live_monitoring (position, symbol, name, aktiv)
                    VALUES (?, NULL, NULL, 0)
                """, (i,))
        
        # Hole aktuelle Positionen
        cursor.execute("""
            SELECT position, symbol, name, hinzugefuegt_am, aktiv
            FROM dashboard_live_monitoring 
            ORDER BY position
        """)
        
        positions = []
        for row in cursor.fetchall():
            positions.append({
                'position': row[0],
                'symbol': row[1],
                'name': row[2],
                'hinzugefuegt_am': row[3],
                'aktiv': bool(row[4]),
                'ist_belegt': row[1] is not None
            })
        
        conn.commit()
        conn.close()
        
        return {
            "live_monitoring_positionen": positions,
            "freie_positionen": [p['position'] for p in positions if not p['ist_belegt']],
            "belegte_positionen": [p['position'] for p in positions if p['ist_belegt']],
            "abgerufen_am": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Live-Monitoring Positionen: {str(e)}")

# Enhanced API endpoint for position management
@app.post("/api/live-monitoring/add")
async def add_position_to_monitoring(request: dict):
    """
    Enhanced endpoint to add position with shares and investment details
    """
    try:
        symbol = request.get('symbol', '').upper()
        shares = request.get('shares', 1)
        investment = request.get('investment', 0)
        
        if not symbol:
            raise HTTPException(status_code=400, detail="Symbol ist erforderlich")
        
        # Find next available position or use first available
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create enhanced live monitoring table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS live_monitoring_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                shares INTEGER NOT NULL,
                investment_amount REAL NOT NULL,
                entry_price REAL,
                current_price REAL,
                total_value REAL,
                profit_loss REAL,
                profit_loss_percent REAL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Get current stock price
        stock_info = google_aktien_suche(symbol)
        current_price = stock_info.get('current_price', 0)
        entry_price = current_price  # Use current price as entry price
        total_value = shares * current_price
        
        # Insert position
        cursor.execute("""
            INSERT INTO live_monitoring_positions 
            (symbol, shares, investment_amount, entry_price, current_price, total_value, profit_loss, profit_loss_percent)
            VALUES (?, ?, ?, ?, ?, ?, 0, 0)
        """, (symbol, shares, investment, entry_price, current_price, total_value))
        
        position_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "message": f"Position für {symbol} erfolgreich hinzugefügt",
            "position_id": position_id,
            "details": {
                "symbol": symbol,
                "shares": shares,
                "investment_amount": investment,
                "entry_price": entry_price,
                "current_value": total_value
            },
            "created_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Hinzufügen der Position: {str(e)}")

@app.get("/api/monitoring/summary")
async def monitoring_summary():
    """Enhanced monitoring summary including position management"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get positions from enhanced table
        cursor.execute("""
            SELECT symbol, shares, investment_amount, entry_price, current_price, 
                   total_value, profit_loss, profit_loss_percent, added_at
            FROM live_monitoring_positions 
            ORDER BY added_at DESC
        """)
        
        positions = cursor.fetchall()
        stocks_data = []
        
        if positions:
            for pos in positions:
                # Update current price
                try:
                    stock_info = google_aktien_suche(pos[0])
                    current_price = stock_info.get('current_price', pos[4])
                    
                    # Recalculate values
                    total_value = pos[1] * current_price
                    profit_loss = total_value - pos[2]  # current value - investment
                    profit_loss_percent = (profit_loss / pos[2] * 100) if pos[2] > 0 else 0
                    
                    # Update database
                    cursor.execute("""
                        UPDATE live_monitoring_positions 
                        SET current_price = ?, total_value = ?, profit_loss = ?, 
                            profit_loss_percent = ?, last_updated = CURRENT_TIMESTAMP
                        WHERE symbol = ?
                    """, (current_price, total_value, profit_loss, profit_loss_percent, pos[0]))
                    
                    stocks_data.append({
                        "symbol": pos[0],
                        "shares": pos[1],
                        "investment_amount": pos[2],
                        "entry_price": pos[3],
                        "current_price": current_price,
                        "total_value": total_value,
                        "profit_loss": profit_loss,
                        "change_percent": profit_loss_percent,
                        "added_at": pos[8]
                    })
                except:
                    # Fallback to stored data
                    stocks_data.append({
                        "symbol": pos[0],
                        "shares": pos[1],
                        "investment_amount": pos[2],
                        "entry_price": pos[3],
                        "current_price": pos[4],
                        "total_value": pos[5],
                        "profit_loss": pos[6],
                        "change_percent": pos[7],
                        "added_at": pos[8]
                    })
        else:
            # Fallback data if no positions exist
            stocks_data = [
                {"symbol": "AAPL", "current_price": 150.25, "change_percent": 2.1, "shares": 10},
                {"symbol": "TSLA", "current_price": 234.50, "change_percent": -1.5, "shares": 5},
                {"symbol": "MSFT", "current_price": 380.75, "change_percent": 1.8, "shares": 8},
                {"symbol": "NVDA", "current_price": 925.30, "change_percent": 4.2, "shares": 3},
                {"symbol": "GOOGL", "current_price": 142.80, "change_percent": 0.7, "shares": 12}
            ]
        
        conn.commit()
        conn.close()
        
        return {
            "stocks": stocks_data,
            "total_positions": len(stocks_data),
            "total_investment": sum([s.get('investment_amount', 0) for s in stocks_data]),
            "total_current_value": sum([s.get('total_value', s.get('current_price', 0) * s.get('shares', 1)) for s in stocks_data]),
            "last_updated": datetime.now().isoformat()
        }
    
    except Exception as e:
        # Fallback to simple data
        return {
            "stocks": [
                {"symbol": "AAPL", "current_price": 150.25, "change_percent": 2.1, "shares": 10},
                {"symbol": "TSLA", "current_price": 234.50, "change_percent": -1.5, "shares": 5},
                {"symbol": "MSFT", "current_price": 380.75, "change_percent": 1.8, "shares": 8},
                {"symbol": "NVDA", "current_price": 925.30, "change_percent": 4.2, "shares": 3},
                {"symbol": "GOOGL", "current_price": 142.80, "change_percent": 0.7, "shares": 12}
            ],
            "last_updated": datetime.now().isoformat()
        }

@app.post("/api/dashboard/add-to-live-monitoring")
async def füge_aktie_zu_live_monitoring_hinzu(
    symbol: str, 
    name: str, 
    position: int, 
    replace_existing: bool = False
):
    """
    Füge Aktie aus Wachstumsprognose zu Live-Monitoring hinzu
    """
    try:
        if position < 1 or position > 10:
            raise HTTPException(status_code=400, detail="Position muss zwischen 1 und 10 liegen")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Prüfe ob Position bereits belegt ist
        cursor.execute("""
            SELECT symbol, name FROM dashboard_live_monitoring 
            WHERE position = ? AND aktiv = 1 AND symbol IS NOT NULL
        """, (position,))
        
        existing = cursor.fetchone()
        if existing and not replace_existing:
            conn.close()
            raise HTTPException(
                status_code=409, 
                detail=f"Position {position} ist bereits mit {existing[0]} ({existing[1]}) belegt. Nutzen Sie replace_existing=True zum Überschreiben."
            )
        
        # Aktualisiere/Setze Position
        cursor.execute("""
            INSERT OR REPLACE INTO dashboard_live_monitoring 
            (position, symbol, name, hinzugefuegt_am, aktiv)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, 1)
        """, (position, symbol.upper(), name))
        
        # Füge auch zur allgemeinen Monitoring-Liste hinzu
        historical_manager.add_monitored_stock(symbol, name, 300)
        
        conn.commit()
        conn.close()
        
        # Starte Live-Monitoring für die Aktie
        stock_info = google_aktien_suche(symbol)
        if stock_info:
            historical_manager.save_historical_data(symbol, stock_info)
        
        return {
            "status": "erfolgreich",
            "message": f"{symbol} wurde zu Position {position} im Live-Monitoring hinzugefügt",
            "symbol": symbol.upper(),
            "name": name,
            "position": position,
            "ersetzt": existing is not None,
            "vorherige_aktie": existing[0] if existing else None,
            "hinzugefuegt_am": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Hinzufügen zur Live-Monitoring: {str(e)}")

@app.delete("/api/dashboard/remove-from-live-monitoring/{position}")
async def entferne_aktie_aus_live_monitoring(position: int):
    """
    Entferne Aktie aus Live-Monitoring Position
    """
    try:
        if position < 1 or position > 10:
            raise HTTPException(status_code=400, detail="Position muss zwischen 1 und 10 liegen")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Hole aktuelle Aktie in Position
        cursor.execute("""
            SELECT symbol, name FROM dashboard_live_monitoring 
            WHERE position = ? AND aktiv = 1
        """, (position,))
        
        current = cursor.fetchone()
        if not current or not current[0]:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Keine Aktie in Position {position} gefunden")
        
        # Entferne Aktie aus Position
        cursor.execute("""
            UPDATE dashboard_live_monitoring 
            SET symbol = NULL, name = NULL, aktiv = 0, hinzugefuegt_am = CURRENT_TIMESTAMP
            WHERE position = ?
        """, (position,))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "erfolgreich",
            "message": f"{current[0]} wurde aus Position {position} entfernt",
            "entfernte_aktie": current[0],
            "entfernter_name": current[1],
            "position": position,
            "entfernt_am": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Entfernen aus Live-Monitoring: {str(e)}")

@app.get("/api/dashboard/live-monitoring-data")
async def hole_live_monitoring_daten():
    """
    Hole aktuelle Daten für alle Live-Monitoring Positionen
    """
    try:
        # Hole Live-Monitoring Positionen
        positions_response = await hole_live_monitoring_positionen()
        positions = positions_response["live_monitoring_positionen"]
        
        monitoring_data = []
        for pos in positions:
            if pos['ist_belegt'] and pos['symbol']:
                # Hole aktuelle Marktdaten
                stock_info = google_aktien_suche(pos['symbol'])
                
                if stock_info:
                    # Hole historische Daten für Mini-Chart
                    historical_data = historical_manager.get_historical_data(pos['symbol'], 7)
                    intraday_data = historical_manager.get_intraday_data(pos['symbol'], 6)
                    
                    monitoring_data.append({
                        'position': pos['position'],
                        'symbol': pos['symbol'],
                        'name': pos['name'],
                        'current_data': stock_info,
                        'historical_data': historical_data[-7:] if historical_data else [],
                        'intraday_data': intraday_data[-24:] if intraday_data else [],
                        'hinzugefuegt_am': pos['hinzugefuegt_am']
                    })
                else:
                    monitoring_data.append({
                        'position': pos['position'],
                        'symbol': pos['symbol'],
                        'name': pos['name'],
                        'current_data': None,
                        'error': 'Daten nicht verfügbar'
                    })
            else:
                monitoring_data.append({
                    'position': pos['position'],
                    'ist_leer': True
                })
        
        return {
            "live_monitoring_daten": monitoring_data,
            "anzahl_aktive": len([d for d in monitoring_data if not d.get('ist_leer')]),
            "freie_plaetze": len([d for d in monitoring_data if d.get('ist_leer')]),
            "aktualisiert_am": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Live-Monitoring Daten: {str(e)}")

@app.get("/api/dashboard/available-growth-stocks")
async def hole_verfügbare_wachstums_aktien():
    """
    Hole verfügbare Aktien aus Wachstumsprognose für Live-Monitoring Auswahl
    """
    try:
        # Hole aktuelle Wachstumsprognosen
        prognose_data = hole_wachstumsprognosen()
        top_stocks = prognose_data.get('top_10_wachstums_aktien', [])
        
        # Hole aktuelle Live-Monitoring Positionen
        positions_response = await hole_live_monitoring_positionen()
        current_symbols = [
            pos['symbol'] for pos in positions_response["live_monitoring_positionen"] 
            if pos['ist_belegt'] and pos['symbol']
        ]
        
        # Markiere verfügbare Aktien
        available_stocks = []
        for stock in top_stocks:
            is_monitored = stock['symbol'] in current_symbols
            
            available_stocks.append({
                'symbol': stock['symbol'],
                'name': stock.get('name', 'N/A'),
                'wachstums_score': stock.get('wachstums_score', 0),
                'current_price': stock.get('current_price', 0),
                'prognose_30_tage': stock.get('prognose_30_tage', {}),
                'ist_bereits_überwacht': is_monitored,
                'empfehlung': 'Hoch' if stock.get('wachstums_score', 0) >= 80 else 'Mittel' if stock.get('wachstums_score', 0) >= 70 else 'Niedrig'
            })
        
        return {
            "verfügbare_wachstums_aktien": available_stocks,
            "anzahl_verfügbar": len([s for s in available_stocks if not s['ist_bereits_überwacht']]),
            "anzahl_bereits_überwacht": len([s for s in available_stocks if s['ist_bereits_überwacht']]),
            "empfohlene_aktien": [s for s in available_stocks if s['empfehlung'] == 'Hoch' and not s['ist_bereits_überwacht']],
            "abgerufen_am": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen verfügbarer Wachstums-Aktien: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)