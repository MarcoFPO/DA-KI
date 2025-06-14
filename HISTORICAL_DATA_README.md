# DA-KI Historical Stock Data System

## Übersicht

Das DA-KI Projekt wurde um ein umfassendes **Historical Stock Data System** erweitert, das Live-Monitoring von Aktien mit zeitlichem Verlauf und tagesaktueller Datenspeicherung in einer SQLite-Datenbank ermöglicht.

## ✨ Neue Features

### 📊 Historische Datenspeicherung
- **Tägliche Kursdaten**: Open, High, Low, Close, Volume, Market Cap, P/E Ratio
- **Intraday-Daten**: 5-Minuten-Intervalle für Live-Tracking
- **Automatische Timestamps**: Alle Daten werden mit Datum und Uhrzeit gespeichert
- **Portfolio-Tracking**: Mehrere Aktien gleichzeitig überwachen

### 🔄 Live-Monitoring System
- **Überwachte Aktien**: Liste von Aktien die kontinuierlich getrackt werden
- **Konfigurierbares Intervall**: Standard 5-Minuten, anpassbar pro Aktie
- **Background Tasks**: Automatische Datensammlung im Hintergrund
- **Echtzeit-Updates**: Integration mit bestehender Google Search API

### 📈 Analytische Funktionen
- **Statistiken**: Min/Max/Average Preise, Volatilität, Trends
- **Zeitraum-Analysen**: 30-Tage Trends, Performance-Vergleiche
- **Portfolio-Analysen**: Historische Daten für mehrere Aktien
- **Datenbereinigung**: Automatisches Löschen alter Daten

## 🗃️ Datenbank-Schema

### Neue Tabellen

#### `historical_stock_data`
```sql
CREATE TABLE historical_stock_data (
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
);
```

#### `intraday_stock_data`
```sql
CREATE TABLE intraday_stock_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    price REAL NOT NULL,
    volume INTEGER,
    change_amount REAL,
    change_percent TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timestamp)
);
```

#### `monitored_stocks`
```sql
CREATE TABLE monitored_stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    monitoring_interval INTEGER DEFAULT 300,
    letztes_update TIMESTAMP,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔗 API-Endpoints

### Historische Daten

#### `GET /api/historical/{symbol}?days=30`
Hole historische Daten für eine Aktie
```json
{
  "symbol": "AAPL",
  "zeitraum_tage": 30,
  "anzahl_datenpunkte": 25,
  "historische_daten": [
    {
      "datum": "2025-06-13",
      "close_price": 195.89,
      "change_amount": 2.34,
      "change_percent": "+1.21%",
      "market_cap": "3.04T",
      "pe_ratio": "31.2"
    }
  ]
}
```

#### `GET /api/intraday/{symbol}?hours=24`
Hole Intraday-Daten (5-Minuten-Intervalle)
```json
{
  "symbol": "AAPL",
  "zeitraum_stunden": 24,
  "intraday_daten": [
    {
      "timestamp": "2025-06-13T13:30:00",
      "price": 195.89,
      "change_amount": 2.34,
      "change_percent": "+1.21%"
    }
  ]
}
```

### Monitoring-Verwaltung

#### `GET /api/monitored-stocks`
Liste aller überwachten Aktien
```json
{
  "überwachte_aktien": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "is_active": true,
      "monitoring_interval": 300,
      "letztes_update": "2025-06-13T13:30:00"
    }
  ]
}
```

#### `POST /api/monitored-stocks`
Füge neue Aktie zur Überwachung hinzu
```bash
curl -X POST "http://localhost:8003/api/monitored-stocks" \
  -d "symbol=TSLA&name=Tesla Inc.&monitoring_interval=300"
```

### Portfolio & Statistiken

#### `GET /api/portfolio-historical?symbols=AAPL,TSLA,NVDA&days=30`
Historische Daten für Portfolio
```json
{
  "portfolio_symbole": ["AAPL", "TSLA", "NVDA"],
  "portfolio_daten": {
    "AAPL": [...],
    "TSLA": [...],
    "NVDA": [...]
  }
}
```

#### `GET /api/statistics/{symbol}`
Detaillierte Statistiken
```json
{
  "symbol": "AAPL",
  "statistiken": {
    "anzahl_tage": 30,
    "min_preis": 180.25,
    "max_preis": 198.50,
    "avg_preis": 190.75,
    "volatilität": 5.67,
    "30_tage_trend": 2.5
  }
}
```

### Live-Monitoring

#### `GET /api/live-monitoring/start/{symbol}`
Startet kontinuierliches Live-Monitoring
```json
{
  "status": "Live-Monitoring gestartet",
  "symbol": "AAPL",
  "interval": "5 Minuten",
  "gestartet_am": "2025-06-13T13:30:00"
}
```

## 🚀 Installation & Setup

### 1. System initialisieren
```bash
cd /home/mdoehler/data-web-app
python3 scripts/init_historical_monitoring.py
```

### 2. API starten
```bash
python3 api/api_top10_final.py
```

### 3. Standard-Aktien sind automatisch konfiguriert:
- AAPL (Apple Inc.)
- TSLA (Tesla Inc.)
- NVDA (NVIDIA Corporation)
- MSFT (Microsoft Corporation)
- GOOGL (Alphabet Inc.)
- PLTR (Palantir Technologies Inc.)
- ENPH (Enphase Energy Inc.)
- AMD (Advanced Micro Devices Inc.)
- NFLX (Netflix Inc.)
- META (Meta Platforms Inc.)

## 🔧 Konfiguration

### Monitoring-Intervalle
- **Standard**: 300 Sekunden (5 Minuten)
- **Anpassbar**: Pro Aktie individuell konfigurierbar
- **Minimum**: 60 Sekunden (1 Minute)

### Datenaufbewahrung
- **Historische Daten**: 90 Tage (Standard)
- **Intraday-Daten**: 7 Tage (Standard)
- **Automatische Bereinigung**: über `/api/cleanup-data`

## 📊 Integration mit bestehendem System

### Erweiterte Google Search API
Die bestehende `/api/google-suche/{symbol}` Funktion wurde erweitert:
- Speichert automatisch historische Daten
- Erfasst Intraday-Daten
- Aktualisiert Monitoring-Status

### Dashboard-Integration
Das Dash-Dashboard kann die neuen historischen Daten nutzen:
- Zeitreihen-Charts mit historischen Verläufen
- Portfolio-Performance über Zeit
- Trend-Analysen und Volatilitäts-Messungen

## 🎯 Anwendungsfälle

1. **Live-Trading Analyse**: Echtzeit-Tracking mit 5-Minuten-Intervallen
2. **Portfolio-Management**: Historische Performance-Analysen
3. **Trend-Erkennung**: 30-Tage-Trends und Volatilitäts-Messungen
4. **Risk Management**: Statistische Analysen und Risiko-Bewertungen
5. **Backtesting**: Historische Daten für Strategy-Testing

## 🔍 Beispiel-Workflows

### Live-Monitoring starten
```bash
# Starte Live-Monitoring für Tesla
curl http://localhost:8003/api/live-monitoring/start/TSLA

# Prüfe Intraday-Daten nach 30 Minuten
curl http://localhost:8003/api/intraday/TSLA?hours=1
```

### Portfolio-Analyse
```bash
# Hole 30-Tage historische Daten für Tech-Portfolio
curl "http://localhost:8003/api/portfolio-historical?symbols=AAPL,MSFT,NVDA,GOOGL&days=30"

# Analysiere Statistiken
curl http://localhost:8003/api/statistics/AAPL
```

### Datenbereinigung
```bash
# Bereinige Daten älter als 60 Tage
curl -X POST "http://localhost:8003/api/cleanup-data" \
  -d "keep_days=60&keep_intraday_days=5"
```

## 🛠️ Technische Details

### Performance-Optimierungen
- **Datenbank-Indizes**: Optimiert für Symbol + Datum/Timestamp Abfragen
- **Unique Constraints**: Verhindert Duplikate bei gleichzeitigen Anfragen
- **Background Tasks**: Async Processing für Live-Monitoring
- **Caching**: Integration mit bestehendem 1-Stunden Cache

### Error Handling
- **Fallback-Mechanismen**: Bei API-Fehlern
- **Datenvalidierung**: Automatische Bereinigung ungültiger Daten
- **Logging**: Umfassende Fehlerprotokollierung

### Skalierbarkeit
- **SQLite für Entwicklung**: Einfache Einrichtung und Wartung
- **PostgreSQL-ready**: Schema ist kompatibel für Production-Upgrade
- **Horizontal Scaling**: Background Tasks können auf mehrere Worker verteilt werden

## 📋 Wartung

### Regelmäßige Aufgaben
1. **Datenbereinigung**: Wöchentlich alte Daten löschen
2. **Index-Optimierung**: Monatlich VACUUM und ANALYZE
3. **Monitoring-Review**: Nicht mehr benötigte Aktien deaktivieren

### Backup-Strategie
```bash
# Datenbank-Backup
cp database/aktienanalyse_de.db backup/aktienanalyse_$(date +%Y%m%d).db

# Nur historische Daten exportieren
sqlite3 database/aktienanalyse_de.db ".dump historical_stock_data" > backup/historical_$(date +%Y%m%d).sql
```

---

## 🎉 Fazit

Das DA-KI Historical Stock Data System erweitert das bestehende Aktienanalyse-System um umfassende zeitliche Datenverfolgung und ermöglicht:

✅ **Automatische Datenspeicherung** mit zeitlichem Verlauf  
✅ **Live-Monitoring** mit 5-Minuten-Intervallen  
✅ **Portfolio-Analysen** mit historischen Trends  
✅ **Statistische Auswertungen** und Volatilitäts-Messungen  
✅ **Nahtlose Integration** mit bestehendem AI-Prognosesystem  

Das System ist production-ready und kann sofort mit den konfigurierten Standard-Aktien verwendet werden.