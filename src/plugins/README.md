# DA-KI Plugin System

Das DA-KI Plugin System bietet eine erweiterbare Architektur für die Integration verschiedener Finanzmarktdatenquellen. Es unterstützt sowohl kostenlose als auch Premium-Datenquellen mit einheitlichen APIs.

## 🎯 Überblick

### Unterstützte Datenquellen

| Plugin | Typ | API-Key | Kostenlos | Premium | Hauptfeatures |
|--------|-----|---------|-----------|---------|---------------|
| **Alpha Vantage** | Premium | ✅ | 500 calls/Tag | Unbegrenzt | OHLCV, Indikatoren, Forex, Crypto |
| **Yahoo Finance** | Kostenlos | ❌ | ✅ | - | OHLCV, News, Dividenden, Splits |
| **FRED** | Kostenlos | ✅ | ✅ | - | Makroökonomische Daten |
| **Financial Modeling Prep** | Premium | ✅ | 250 calls/Tag | 300+ calls/Min | Finanzberichte, Analysten-Schätzungen |
| **Reddit Sentiment** | Kostenlos | ✅ | ✅ | - | Social Media Sentiment |
| **News Sentiment** | Mixed | ✅ | Begrenzt | Premium | Multi-Source News Sentiment |

## 🚀 Schnellstart

### 1. Demo ausführen

```bash
# Ohne Abhängigkeiten - zeigt Plugin-Funktionalität
python3 src/plugins/plugin_manager_demo.py
```

### 2. Vollständige Installation

```bash
# Abhängigkeiten installieren
pip install aiohttp pydantic python-dateutil

# Tests ausführen (nach API-Key-Konfiguration)
python3 -m src.plugins.test_plugin_manager
```

### 3. Basis-Setup (nur kostenlose APIs)

```python
from src.plugins.plugin_manager import PluginManager

# Plugin Manager initialisieren
pm = PluginManager()
await pm.load_plugins()

# Yahoo Finance Plugin aktivieren (kein API-Key nötig)
config = {
    "rate_limit_delay": 0.1,
    "enable_news": True
}
await pm.configure_plugin("YahooFinancePlugin", config)

# Daten abrufen
data = await pm.fetch_data_from_plugin(
    "YahooFinancePlugin",
    "ohlcv", 
    "AAPL",
    "2024-01-01",
    "2024-01-31"
)
print(f"Erhalten: {len(data)} Datensätze")
```

## 🔧 Konfiguration

### Plugin-Konfiguration

Jedes Plugin hat ein eigenes Konfigurationsschema:

```python
# Konfigurationsschema anzeigen
schema = pm.get_plugin_config_schema("AlphaVantagePlugin")
for param, details in schema.items():
    print(f"{param}: {details['description']}")
```

### Beispiel-Konfigurationen

Siehe [`example_plugin_config.json`](./example_plugin_config.json) für vollständige Konfigurationsbeispiele.

#### Alpha Vantage (Premium)
```python
config = {
    "api_key": "YOUR_ALPHA_VANTAGE_KEY",
    "rate_limit_delay": 12.0,  # Free tier: 5 calls/min
    "premium_account": False
}
```

#### FRED (Kostenlos)
```python
config = {
    "api_key": "YOUR_FRED_API_KEY",  # Kostenlos unter fred.stlouisfed.org
    "rate_limit_delay": 0.5,
    "default_frequency": "d"
}
```

#### Reddit Sentiment (Kostenlos)
```python
config = {
    "client_id": "YOUR_REDDIT_CLIENT_ID",
    "client_secret": "YOUR_REDDIT_SECRET",
    "user_agent": "DA-KI:v1.0 (by /u/your_username)",
    "target_subreddits": ["stocks", "investing"]
}
```

## 📊 Datentypen

### OHLCV Daten
```python
# Tägliche Kursdaten
data = await pm.fetch_data_from_plugin(
    "YahooFinancePlugin",
    "ohlcv",
    "AAPL",
    "2024-01-01",
    "2024-01-31",
    interval="daily"
)
```

### Technische Indikatoren
```python
# Finanzielle Kennzahlen
indicators = await pm.fetch_data_from_plugin(
    "FinancialModelingPrepPlugin",
    "indicators",
    "AAPL",
    "2024-01-01",
    "2024-01-31",
    indicator_type="financial_ratios",
    params={"limit": 5}
)
```

### Event-Daten
```python
# Nachrichten und Events
events = await pm.fetch_data_from_plugin(
    "NewsSentimentPlugin",
    "events",
    "AAPL",
    "2024-01-01",
    "2024-01-31",
    event_type="company_news"
)
```

### Parallele Datenabfrage
```python
# Daten von allen aktiven Plugins
all_data = await pm.fetch_data_from_all_active_plugins(
    "ohlcv",
    "AAPL", 
    "2024-01-01",
    "2024-01-31"
)

for plugin_name, data in all_data.items():
    print(f"{plugin_name}: {len(data)} Datensätze")
```

## 🔒 Sicherheit

### API-Key Management
```bash
# Umgebungsvariablen verwenden
export ALPHA_VANTAGE_API_KEY="your_key_here"
export FRED_API_KEY="your_key_here"

# In Python
import os
config = {
    "api_key": os.getenv("ALPHA_VANTAGE_API_KEY"),
    "rate_limit_delay": 12.0
}
```

### Rate Limiting
- Jedes Plugin implementiert eigenes Rate Limiting
- Konfigurierbare Delays zwischen API-Calls
- Automatische Retry-Logik mit exponential backoff
- Parallelausführung mit Respektierung der Limits

### Logging
```python
import logging
logging.basicConfig(level=logging.INFO)

# Plugin-spezifische Logs
logger = logging.getLogger("src.plugins.alpha_vantage_plugin")
logger.setLevel(logging.DEBUG)
```

## 🧪 Tests und Entwicklung

### Plugin-Status prüfen
```python
status = pm.get_status()
print(f"Aktive Plugins: {status['details']['active_plugins']}")

for plugin_name, plugin_status in status['details']['plugins'].items():
    print(f"{plugin_name}: {plugin_status['status']}")
```

### Plugin entwickeln

Neue Plugins müssen von `DataSourcePlugin` erben:

```python
from src.plugins.data_sources.data_source_plugin import DataSourcePlugin

class MyCustomPlugin(DataSourcePlugin):
    def get_name(self) -> str:
        return "MyCustomPlugin"
    
    def get_description(self) -> str:
        return "My custom data source"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "api_key": {
                "type": "string",
                "required": True,
                "sensitive": True
            }
        }
    
    # Implementiere fetch_ohlcv_data, fetch_technical_indicators, fetch_event_data
```

## 📈 Performance-Optimierung

### Parallele Ausführung
```python
import asyncio

# Mehrere Ticker parallel
tickers = ["AAPL", "MSFT", "GOOGL"]
tasks = [
    pm.fetch_data_from_plugin("YahooFinancePlugin", "ohlcv", ticker, start, end)
    for ticker in tickers
]
results = await asyncio.gather(*tasks)
```

### Caching
```python
# Plugin-Level Caching implementieren
class CachedPlugin(DataSourcePlugin):
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 Minuten
```

### Fehlerbehandlung
```python
try:
    data = await pm.fetch_data_from_plugin(...)
    if not data:
        print("Keine Daten erhalten - prüfe Konfiguration")
except Exception as e:
    print(f"Fehler: {e}")
    # Fallback auf anderen Plugin
```

## 🛠️ Troubleshooting

### Häufige Probleme

**401/403 Fehler**
- API-Key prüfen
- API-Key-Gültigkeit überprüfen
- Rate Limits beachten

**429 Rate Limit Exceeded**
- `rate_limit_delay` erhöhen
- Weniger parallele Requests
- Premium-Plan erwägen

**Keine Daten**
- Ticker-Symbol prüfen
- Datumsbereich anpassen
- Mit bekannten Symbolen testen (AAPL, MSFT)

**Import-Fehler**
```bash
pip install aiohttp pydantic python-dateutil
```

### Debug-Modus
```python
import logging
logging.getLogger("src.plugins").setLevel(logging.DEBUG)
```

## 🤝 Beitragen

1. Fork das Repository
2. Erstelle einen Feature-Branch
3. Implementiere neues Plugin nach `DataSourcePlugin` Interface
4. Füge Tests hinzu
5. Erstelle Pull Request

## 📄 Lizenz

Siehe Haupt-Repository für Lizenzinformationen.

## 🔗 Nützliche Links

- [Alpha Vantage API](https://www.alphavantage.co/documentation/)
- [FRED API](https://research.stlouisfed.org/docs/api/fred/)
- [Reddit API](https://www.reddit.com/dev/api/)
- [Financial Modeling Prep](https://financialmodelingprep.com/developer/docs)
- [NewsAPI](https://newsapi.org/docs)
- [Yahoo Finance (Unofficial)](https://python-yahoofinance.readthedocs.io/)