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

## 🏗️ Modulare Architektur

```
DA-KI/
├── 📁 frontend/          # Modulares Web-Interface (Vollständig isoliert)
│   ├── dashboard_orchestrator.py      # Hauptkoordinator
│   ├── frontend_layout_module.py      # Layout-Komponenten
│   ├── frontend_tabelle_module.py     # Tabellen mit Action-Buttons
│   ├── frontend_callback_module.py    # Event-Management
│   ├── ki_wachstumsprognose_module.py # KI-Algorithmen (isoliert)
│   └── live_monitoring_module.py      # Portfolio-Management (isoliert)
├── 📁 api/              # FastAPI Backend
├── 📁 services/         # Core Business Logic
├── 📁 database/         # SQLite Datenbank
├── 📁 docs/            # Dokumentation
└── 📁 tests/           # Test Suite
```

### 🧩 Teilprojekte (Modulare Architektur)

| Komponente | Beschreibung | Status |
|------------|-------------|---------|
| **CORE** | Berechnungs-Engine & KI-Algorithmen | ✅ Aktiv |
| **FRONTEND** | **Vollständig modulare UI-Architektur** | ✅ **Modular** |
| **KI-WACHSTUMSPROGNOSE** | Isoliertes Modul mit definierten Schnittstellen | ✅ **Isoliert** |
| **LIVE-MONITORING** | Isoliertes Portfolio-Management Modul | ✅ **Isoliert** |
| **DEPO-STEUERUNG** | Portfolio-Management | 📋 Geplant |

### 🎯 **Neue Modulare Features**
- **🔗 Dependency Injection**: Cross-Module Kommunikation
- **🛡️ Fehler-Isolation**: Module beeinträchtigen sich nicht
- **🧩 Interface-Driven**: Definierte Schnittstellen zwischen Modulen
- **⚡ Orchestrator-Pattern**: Zentrale Koordination aller Module
- **📋 Action-Button Integration**: Vollständig funktionale Tabellen-Actions

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

- **Dashboard**: http://10.1.1.110:8054
- **API Dokumentation**: http://10.1.1.110:8003/docs
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

## 📈 Strategische Roadmap

### 🎯 Konzeptstruktur
- **[Konzept-Übersicht](docs/CONCEPT_OVERVIEW.md)** - Strategische Gesamtausrichtung
- **[Business Konzept](docs/BUSINESS_CONCEPT.md)** - Geschäftsmodell & Marktanalyse  
- **[Technical Konzept](docs/TECHNICAL_CONCEPT.md)** - Architektur & Implementation
- **[Implementation Roadmap](docs/IMPLEMENTATION_ROADMAP.md)** - Strukturierte Umsetzung

### Phase 1: Foundation (✅ Größtenteils Abgeschlossen)
- [x] Core KI-Algorithmus mit 5-Faktor Scoring
- [x] Enhanced Live-Monitoring mit Position-Selection Modal
- [x] Vollständiges GitHub Projektmanagement Setup
- [x] Professionelle Dokumentations-Suite

### Phase 2: Scale & Performance (🚧 In Arbeit)
- [ ] Real-time Yahoo Finance API Integration
- [ ] AsyncIO Parallel Processing (467 Aktien <5s)
- [ ] Redis Multi-Level Caching System
- [ ] WebSocket Real-time Updates
- [ ] PostgreSQL Migration & Optimization

### Phase 3: Growth & Expansion (📋 Q4 2025)
- [ ] DACH-Region Expansion (AT/CH Märkte)
- [ ] Advanced Portfolio-Optimierung
- [ ] Mobile App (React Native)
- [ ] B2B API Platform & White-Label Solutions

### Phase 4: Enterprise & Global (📅 2026)
- [ ] International Markets (UK/US)
- [ ] Enterprise-Grade Features
- [ ] AI Innovation (GPT Integration)
- [ ] Series A Fundraising

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