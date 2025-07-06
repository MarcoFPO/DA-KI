# Kostenlose und günstige Datenquellen-Plugins

Diese Liste fokussiert sich auf **kostenlose** und **günstige Freemium-APIs** für eine budgetfreundliche Implementierung.

## 🟢 Völlig kostenlose APIs (Priorität 1)

### Regierungsdaten und Zentralbanken
| Plugin | Quelle | Daten | Rate Limit |
|--------|--------|-------|------------|
| **SECFilingsPlugin** | US SEC | 10-K, 10-Q, 8-K Berichte | Unbegrenzt |
| **ECBDataPlugin** | Europäische Zentralbank | EUR Geldpolitik, Zinsen | Unbegrenzt |
| **BOJDataPlugin** | Bank of Japan | JPY Geldpolitik | Unbegrenzt |
| **BOEDataPlugin** | Bank of England | GBP Geldpolitik | Unbegrenzt |
| **RBIIndiaPlugin** | Reserve Bank India | INR Geldpolitik | Unbegrenzt |
| **OECDDataPlugin** | OECD | Globale Wirtschaftsdaten | Unbegrenzt |
| **WorldBankPlugin** | Weltbank | Entwicklungsdaten | Unbegrenzt |
| **IMFDataPlugin** | IMF | Internationale Finanzen | Unbegrenzt |
| **EurostatPlugin** | EU Statistikamt | EU Wirtschaftsdaten | Unbegrenzt |

### Open Source Bibliotheken
| Plugin | Typ | Features | Kosten |
|--------|-----|----------|--------|
| **TaLibPlugin** | Technische Analyse | 150+ Indikatoren | Kostenlos |
| **YFinancePlugin** | Yahoo Finance (Unofficial) | OHLCV, News | Kostenlos |
| **PandasDataReaderPlugin** | Multi-Source | FRED, OECD, Yahoo | Kostenlos |
| **InvestpyPlugin** | Multi-Market | Global Indizes | Kostenlos |

### Krypto (Open APIs)
| Plugin | Quelle | Features | Limit |
|--------|--------|----------|-------|
| **CoinGeckoPubPlugin** | CoinGecko Public | Basic Preise | 50 calls/min |
| **CryptoComparePubPlugin** | CryptoCompare | Historische Daten | 100 calls/hour |
| **CoinCapPlugin** | CoinCap | Real-time Preise | Unbegrenzt |

## 🟡 Günstige Freemium APIs (Priorität 2)

### Hohe kostenlose Kontingente
| Plugin | Kostenlos | Premium | Empfehlung |
|--------|-----------|---------|------------|
| **CoinGeckoPlugin** | 10.000 calls/Monat | $129/Monat | Start kostenlos |
| **FinnhubPlugin** | 60 calls/Min | $24.99/Monat | Start kostenlos |
| **AlphaVantagePlugin** | 500 calls/Tag | $49.99/Monat | Start kostenlos |
| **QuandlPlugin** | 50 calls/Tag | $49/Monat | Start kostenlos |
| **NewsAPIPlugin** | 1.000/Tag | $449/Monat | Start kostenlos |
| **ExchangeRatePlugin** | 1.000/Monat | $9.99/Monat | Start kostenlos |
| **CurrencyLayerPlugin** | 1.000/Monat | $9.99/Monat | Start kostenlos |

### Community/Educational Discounts
| Plugin | Normal | Student/Research | Verfügbarkeit |
|--------|--------|------------------|---------------|
| **BloombergAPIPlugin** | $2.000+/Monat | Kostenlos | Universitäten |
| **RefinitivPlugin** | $1.500+/Monat | Kostenlos | Akademisch |
| **S&PCapitalIQPlugin** | $1.000+/Monat | Kostenlos | Student |

## 🚀 Kostenlose Multi-Market Strategie

### Phase 1: Basis-Setup (€0/Monat)
```python
free_plugins = [
    "SECFilingsPlugin",      # US Fundamentaldaten
    "ECBDataPlugin",         # EU Wirtschaftsdaten  
    "YFinancePlugin",        # Globale OHLCV
    "CoinCapPlugin",         # Krypto Basis
    "TaLibPlugin",           # Technische Analyse
    "WorldBankPlugin"        # Makro-Indikatoren
]

# Abdeckung:
# - US Aktien (Fundamentals via SEC)
# - Global OHLCV (via Yahoo)
# - EU/US Makrodaten
# - Basis Krypto
# - Vollständige technische Analyse
```

### Phase 2: Freemium-Upgrade (€0-50/Monat)
```python
freemium_plugins = [
    "CoinGeckoPlugin",       # 10k Krypto calls
    "FinnhubPlugin",         # 86k Stock calls  
    "AlphaVantagePlugin",    # 500 Premium calls/Tag
    "NewsAPIPlugin",         # 30k News calls
    "ExchangeRatePlugin"     # 1k FX calls
]

# Zusätzliche Abdeckung:
# - Umfassende Krypto-Daten
# - Real-time Stock News
# - Premium technische Indikatoren
# - Forex-Daten
```

## 🌍 Kostenlose regionale Märkte

### Direkter Börsen-Zugang (oft kostenlos mit Verzögerung)
| Region | Plugin | Verzögerung | Registrierung |
|--------|--------|-------------|---------------|
| **Deutschland** | **XetraOpenDataPlugin** | 15 Min | Kostenlos |
| **UK** | **LSEOpenDataPlugin** | 15 Min | Kostenlos |
| **Australien** | **ASXOpenDataPlugin** | 20 Min | Kostenlos |
| **Kanada** | **TSXOpenDataPlugin** | 15 Min | Kostenlos |
| **Japan** | **JPXOpenDataPlugin** | 20 Min | Kostenlos |

### Alternative kostenlose Quellen
```python
alternative_free_sources = {
    "investing_com_scraper": {
        "coverage": "Global markets",
        "method": "Web scraping",
        "legal": "Check terms of service"
    },
    "marketwatch_scraper": {
        "coverage": "US markets", 
        "method": "RSS feeds",
        "legal": "Generally allowed"
    },
    "yahoo_finance_scraper": {
        "coverage": "Global markets",
        "method": "Unofficial API",
        "legal": "Gray area"
    }
}
```

## 💡 Kosten-Optimierung Strategien

### 1. API-Rotation
```python
# Rotiere zwischen kostenlosen Limits
rotation_strategy = {
    "morning": "AlphaVantage",    # 500 calls
    "afternoon": "Finnhub",      # 60 calls/min  
    "evening": "CoinGecko",      # 50 calls/min
    "fallback": "YahooFinance"   # Unbegrenzt
}
```

### 2. Intelligentes Caching
```python
cache_strategy = {
    "OHLCV_daily": "24 hours",
    "company_fundamentals": "7 days", 
    "economic_data": "30 days",
    "crypto_prices": "5 minutes"
}
```

### 3. Community Data Sharing
```python
# Nutzer teilen API-Kontingente
community_pool = {
    "shared_api_keys": True,
    "data_contribution": "Upload own data",
    "credits_system": "Earn through sharing"
}
```

## 📊 Kostenlose Data Coverage Analyse

### Mit nur kostenlosen APIs erreichbar:
- **US Aktien**: 100% (SEC + Yahoo)
- **EU Märkte**: 90% (Yahoo + ECB)
- **Asiatische Märkte**: 70% (Yahoo + BoJ)
- **Kryptowährungen**: 95% (Multiple free sources)
- **Forex**: 80% (Zentralbank-Daten)
- **Rohstoffe**: 60% (FRED + Yahoo)
- **Makro-Indikatoren**: 100% (Regierungsquellen)

### Fehlende Features (nur Premium):
- Real-time Daten (meist 15-20 Min Verzögerung)
- Tick-Level Daten
- Advanced Analytics
- Institutional-Grade Support
- API-SLAs

## 🎯 Empfehlung: Start kostenlos

1. **Sofort implementieren**: Alle 15 kostenlosen Plugins
2. **Monat 2-3**: Freemium-Tier testen 
3. **Monat 6+**: Premium nur bei bewiesenem ROI
4. **Langfristig**: Community/Educational Discounts nutzen

Diese Strategie ermöglicht es, mit **€0 Startkosten** eine umfassende globale Finanzmarkt-Datenplattform aufzubauen und erst bei steigendem Nutzerwachstum in Premium-APIs zu investieren.