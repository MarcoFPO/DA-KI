# 🚀 DA-KI - Deutsche Aktienanalyse mit KI-Wachstumsprognose

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Dash](https://img.shields.io/badge/Dash-2.0+-red.svg)](https://dash.plotly.com/)

**Intelligente Aktienanalyse-Plattform mit KI-gestützten Wachstumsprognosen und Live-Monitoring für deutsche Aktienmärkte.**

## 🎯 Projektübersicht

DA-KI ist eine moderne Fintech-Anwendung, die Künstliche Intelligenz nutzt, um deutsche Aktien zu analysieren und Wachstumsprognosen zu erstellen. Die Plattform bietet Echtzeit-Monitoring, Portfolio-Simulation und datengetriebene Investmentempfehlungen.

### ✨ Hauptfunktionen

- **🤖 KI-Wachstumsprognose**: 5-Faktor-Scoring-System für 467+ deutsche Aktien
- **📊 Live-Monitoring**: Echtzeit-Überwachung mit Position-Management
- **💰 Portfolio-Simulation**: KI-optimierte Portfolioallokation
- **📈 Interaktive Dashboards**: Moderne Web-UI mit Dash Framework
- **🔄 API-Integration**: RESTful API mit FastAPI
- **💾 Datenpersistenz**: SQLite-Datenbank mit historischen Daten

## 🏗️ Architektur

```
DA-KI/
├── 📁 frontend/          # Dash Web-Interface
├── 📁 api/              # FastAPI Backend
├── 📁 services/         # Core Business Logic
├── 📁 database/         # SQLite Datenbank
├── 📁 docs/            # Dokumentation
└── 📁 tests/           # Test Suite
```

### 🧩 Teilprojekte

| Komponente | Beschreibung | Status |
|------------|-------------|---------|
| **CORE** | Berechnungs-Engine & KI-Algorithmen | ✅ Aktiv |
| **FRONTEND** | User Interface & Dashboard | ✅ Aktiv |
| **KI-WACHSTUMSPROGNOSE** | Intelligente Analysealgorithmen | ✅ Implementiert |
| **LIVE-MONITORING** | Echtzeit-Datenverarbeitung | 🚧 Enhanced |
| **DEPO-STEUERUNG** | Portfolio-Management | 📋 Geplant |

## 🚀 Quick Start

### Voraussetzungen

```bash
# Python 3.11+
python3 --version

# Abhängigkeiten installieren
pip install fastapi uvicorn dash plotly pandas requests sqlite3
```

### Installation & Start

```bash
# Repository klonen
git clone https://github.com/MarcoFPO/DA-KI.git
cd DA-KI

# API Server starten (Port 8003)
python3 api/api_top10_final.py

# Dashboard starten (Port 8054)
python3 frontend/dashboard_top10.py
```

### 🌐 URLs

- **Dashboard**: http://localhost:8054
- **API Dokumentation**: http://localhost:8003/docs
- **Live Demo**: [Coming Soon]

## 📊 Features im Detail

### KI-Wachstumsprognose
- **5-Faktor-Scoring**: Performance, Marktkapitalisierung, KGV, Sektor, Sentiment
- **467 Deutsche Aktien**: Vollständige DAX, MDAX, SDAX Abdeckung
- **30-Tage Prognosen**: Maschinelles Lernen für Kursprognosen
- **Vertrauens-Scoring**: Risikoeinschätzung pro Prognose

### Live-Monitoring Dashboard
- **🎯 Position-Management**: Interaktive Auswahl mit Modal-Dialogen
- **💹 Echtzeit-Updates**: 60-Sekunden-Intervall für Marktdaten
- **📈 Profit/Loss Tracking**: Automatische Gewinn-/Verlustberechnung
- **🔄 API-Integration**: RESTful Backend-Anbindung

### Portfolio-Simulation
- **KI-Optimierung**: Automatische Allokation basierend auf Wachstumsprognosen
- **Risiko-Management**: Diversifikation nach Sektoren
- **Backtesting**: Historische Performance-Analyse

## 🛠️ Technische Details

### Backend (FastAPI)
```python
# Hauptendpunkte
GET  /api/wachstumsprognose/top10    # Top 10 Wachstumsaktien
POST /api/live-monitoring/add        # Position hinzufügen
GET  /api/monitoring/summary         # Portfolio-Übersicht
```

### Frontend (Dash)
- **Reaktive UI**: Moderne Web-Komponenten
- **Echtzeit-Updates**: WebSocket-ähnliche Updates
- **Mobile-Responsive**: Bootstrap CSS Framework

### Datenbank
```sql
-- Haupttabellen
wachstumsprognosen     # KI-Prognosen
live_monitoring_positions  # Benutzer-Positionen
historical_stock_data  # Historische Kursdaten
```

## 📈 Roadmap

### Phase 1 (✅ Abgeschlossen)
- [x] Core KI-Algorithmus implementiert
- [x] Dashboard mit 3 Hauptbereichen
- [x] Enhanced Button-Funktionalität
- [x] Position-Selection Modal

### Phase 2 (🚧 In Arbeit)
- [ ] Yahoo Finance API Integration
- [ ] AsyncIO Parallel Processing
- [ ] Redis Caching System
- [ ] WebSocket Real-time Updates

### Phase 3 (📋 Geplant)
- [ ] Advanced Portfolio-Steuerung
- [ ] Multi-User Support
- [ ] Docker Containerization
- [ ] Cloud Deployment

## 🤝 Contributing

### Development Setup
```bash
# Development Branch erstellen
git checkout -b feature/neue-funktion

# Tests ausführen
python -m pytest tests/

# Code Style prüfen
flake8 --max-line-length=120

# Commit Guidelines
git commit -m "feat: neue Funktion hinzugefügt

- Beschreibung der Änderungen
- Impact auf bestehende Features

🚀 Generated with [Claude Code](https://claude.ai/code)
"
```

### Issue Templates
- 🐛 **Bug Report**: Fehler melden
- ✨ **Feature Request**: Neue Funktionen vorschlagen  
- 📚 **Documentation**: Dokumentation verbessern
- ⚡ **Performance**: Optimierungen

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe [LICENSE](LICENSE) für Details.

## 🙏 Danksagungen

- **FastAPI**: Hochperformante API-Framework
- **Plotly Dash**: Moderne Dashboard-Entwicklung
- **SQLite**: Zuverlässige Datenpersistenz
- **Claude Code**: KI-gestützte Entwicklung

## 📞 Kontakt

- **Repository**: https://github.com/MarcoFPO/DA-KI
- **Issues**: https://github.com/MarcoFPO/DA-KI/issues
- **Discussions**: https://github.com/MarcoFPO/DA-KI/discussions

---

**🚀 Entwickelt mit [Claude Code](https://claude.ai/code) | MIT License | Python 3.11+ | FastAPI + Dash**