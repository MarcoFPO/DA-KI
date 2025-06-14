# 🤝 Contributing to DA-KI

Vielen Dank für Ihr Interesse an der Mitarbeit am DA-KI Projekt! Diese Anleitung hilft Ihnen bei der Teilnahme an der Entwicklung.

## 🎯 Entwicklungsphilosophie

DA-KI folgt einer modularen, teilprojekt-basierten Entwicklung:
- **CORE**: Robuste Algorithmen und Berechnungen
- **FRONTEND**: Intuitive Benutzeroberflächen  
- **API**: Saubere, dokumentierte Schnittstellen
- **QUALITÄT**: Tests, Code-Reviews, Dokumentation

## 🚀 Quick Start für Entwickler

### 1. Repository Setup
```bash
# Fork erstellen auf GitHub
# Repository klonen
git clone https://github.com/IHR-USERNAME/DA-KI.git
cd DA-KI

# Remote für Original-Repository hinzufügen
git remote add upstream https://github.com/MarcoFPO/DA-KI.git
```

### 2. Development Environment
```bash
# Python Environment (3.11+)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt

# Development Dependencies
pip install pytest flake8 black isort pre-commit
```

### 3. Lokaler Entwicklungsserver
```bash
# API Server (Terminal 1)
python3 api/api_top10_final.py

# Dashboard (Terminal 2)  
python3 frontend/dashboard_top10.py

# URLs
# Dashboard: http://localhost:8054
# API Docs:  http://localhost:8003/docs
```

## 🏗️ Projekt-Struktur

```
DA-KI/
├── 📁 api/                    # FastAPI Backend
│   ├── api_top10_final.py     # Haupt-API Server
│   └── endpoints/             # API Endpunkt-Module
├── 📁 frontend/               # Dash Frontend
│   ├── dashboard_top10.py     # Haupt-Dashboard
│   └── components/            # UI-Komponenten
├── 📁 services/               # Business Logic
│   ├── growth_prediction_top10.py  # KI-Algorithmen
│   └── data_manager.py        # Datenverarbeitung
├── 📁 database/               # Datenpersistenz
│   ├── aktienanalyse_de.db    # SQLite Datenbank
│   └── schemas/               # DB-Schemas
├── 📁 tests/                  # Test Suite
│   ├── test_api.py
│   ├── test_services.py
│   └── test_frontend.py
├── 📁 docs/                   # Dokumentation
└── 📁 scripts/                # Utility Scripts
```

## 📋 Teilprojekte & Zuständigkeiten

### CORE (Berechnungen)
- **Files**: `services/growth_prediction_top10.py`
- **Verantwortlich**: KI-Algorithmen, Scoring-System
- **Skills**: Python, Machine Learning, Finanz-Mathematik

### FRONTEND (User Interface)
- **Files**: `frontend/dashboard_top10.py`, `frontend/components/`
- **Verantwortlich**: Dash-Komponenten, UI/UX
- **Skills**: Python, Dash, HTML/CSS, JavaScript

### API (Backend Services)
- **Files**: `api/api_top10_final.py`, `api/endpoints/`
- **Verantwortlich**: REST API, Datenverarbeitung
- **Skills**: FastAPI, REST, Database Design

### LIVE-MONITORING (Real-time)
- **Files**: API + Frontend Integration
- **Verantwortlich**: WebSockets, Echtzeit-Updates
- **Skills**: AsyncIO, WebSockets, Performance

### DEPO-STEUERUNG (Portfolio)
- **Files**: Neue Module geplant
- **Verantwortlich**: Portfolio-Algorithmen
- **Skills**: Finanz-Algorithmen, Optimierung

## 🔄 Development Workflow

### 1. Issue erstellen/auswählen
```bash
# GitHub Issues verwenden für:
# - 🐛 Bug Reports
# - ✨ Feature Requests  
# - 📚 Documentation
# - ⚡ Performance Improvements
```

### 2. Feature Branch erstellen
```bash
# Naming Convention:
# feat/feature-name     # Neue Features
# fix/bug-description   # Bug Fixes
# docs/update-readme    # Dokumentation
# perf/optimize-api     # Performance

git checkout -b feat/neue-live-monitoring-funktion
```

### 3. Development & Testing
```bash
# Code schreiben
# Tests hinzufügen/aktualisieren
python -m pytest tests/

# Code Style prüfen
flake8 --max-line-length=120
black .
isort .
```

### 4. Commit Guidelines
```bash
# Commit Message Format:
# type(scope): kurze Beschreibung
#
# Längere Beschreibung falls nötig
# - Was wurde geändert
# - Warum wurde es geändert
# - Impact auf andere Komponenten
#
# 🚀 Generated with [Claude Code](https://claude.ai/code)

# Beispiele:
git commit -m "feat(live-monitoring): position selection modal hinzugefügt

- Interactive modal für präzise Position-Auswahl
- Automatische Kurs-Berechnung basierend auf Aktien-Anzahl
- Enhanced API integration für detailliertes Position-Tracking
- Database persistence für Investment-Positionen

🚀 Generated with [Claude Code](https://claude.ai/code)
"

git commit -m "fix(api): fehlerhafte Profit/Loss Berechnung korrigiert"

git commit -m "docs(readme): installation instructions aktualisiert"
```

### 5. Pull Request erstellen
```bash
# Push to your fork
git push origin feat/neue-live-monitoring-funktion

# GitHub PR erstellen mit:
# - Beschreibung der Änderungen
# - Screenshots (bei UI-Änderungen)
# - Test-Ergebnisse
# - Breaking Changes (falls vorhanden)
```

## 🧪 Testing Guidelines

### Unit Tests
```python
# tests/test_growth_prediction.py
def test_wachstums_score_berechnung():
    predictor = WachstumsPredictor()
    score = predictor.berechne_score("AAPL")
    assert 0 <= score <= 100

def test_api_endpoint_wachstumsprognose():
    response = client.get("/api/wachstumsprognose/top10")
    assert response.status_code == 200
    assert len(response.json()["top_10_wachstums_aktien"]) <= 10
```

### Integration Tests
```python
# tests/test_integration.py
def test_button_to_live_monitoring_flow():
    # Test complete user flow from button click to database storage
    pass
```

### Frontend Tests
```python
# tests/test_dashboard.py
def test_modal_dialog_funktionalität():
    # Test modal opening, data input, submission
    pass
```

## 📊 Code Quality Standards

### Python Code Style
```python
# PEP 8 konform mit Ausnahmen:
# - Zeilenlänge: 120 Zeichen (statt 79)
# - String Quotes: Doppelte Anführungszeichen bevorzugt

# Gute Kommentare (Deutsch oder Englisch)
def berechne_wachstums_score(self, aktien_data: Dict) -> float:
    """
    Berechnet den KI-Wachstums-Score für eine Aktie.
    
    Args:
        aktien_data: Dictionary mit Aktiendaten (Kurs, Marktdaten, etc.)
        
    Returns:
        Float zwischen 0-100 (Wachstumspotential)
    """
```

### API Design
```python
# RESTful Endpoints
GET    /api/wachstumsprognose/top10           # Liste abrufen
POST   /api/live-monitoring/add               # Ressource erstellen
GET    /api/live-monitoring/positions/{id}    # Einzelne Ressource
DELETE /api/live-monitoring/positions/{id}    # Ressource löschen

# Konsistente Response Formate
{
    "status": "success",
    "data": { ... },
    "message": "Position erfolgreich hinzugefügt",
    "timestamp": "2025-06-14T08:33:29.110530"
}
```

### Database Design
```sql
-- Konsistente Naming Convention
-- Snake_case für Tabellen und Spalten
-- Timestamps für Audit-Trail
-- Foreign Keys für Referential Integrity

CREATE TABLE live_monitoring_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    shares INTEGER NOT NULL,
    entry_price REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🐛 Bug Reports

### Bug Report Template
```markdown
**Bug Beschreibung**
Kurze, klare Beschreibung des Problems.

**Schritte zur Reproduktion**
1. Gehe zu '...'
2. Klicke auf '....'
3. Scrolle nach unten zu '....'
4. Siehe Fehler

**Erwartetes Verhalten**
Was sollte passieren.

**Tatsächliches Verhalten** 
Was tatsächlich passiert (inkl. Fehlermeldungen).

**Screenshots**
Falls applicable, füge Screenshots hinzu.

**Environment:**
- OS: [z.B. Ubuntu 22.04]
- Python Version: [z.B. 3.11.5]
- Browser: [z.B. Chrome 120]

**Additional Context**
Weitere relevante Informationen.
```

## ✨ Feature Requests

### Feature Request Template
```markdown
**Feature Beschreibung**
Kurze Beschreibung der gewünschten Funktionalität.

**Problem/Use Case**
Welches Problem löst dieses Feature? Welcher Use Case wird abgedeckt?

**Lösung**
Beschreibung der gewünschten Lösung.

**Alternativen**
Alternative Lösungsansätze, die Sie in Betracht gezogen haben.

**Teilprojekt**
Welches Teilprojekt ist betroffen? (CORE, FRONTEND, API, etc.)

**Priority**
- [ ] Low
- [ ] Medium  
- [ ] High
- [ ] Critical
```

## 📚 Dokumentation

### Code Dokumentation
- **Docstrings**: Alle Funktionen und Klassen
- **Type Hints**: Python 3.11+ Type Annotations
- **README Updates**: Bei neuen Features
- **API Docs**: FastAPI automatische Dokumentation

### Architektur-Dokumentation
- **ADR (Architecture Decision Records)**: Wichtige Design-Entscheidungen
- **Sequence Diagrams**: Für komplexe Workflows
- **Database ERD**: Entity Relationship Diagrams

## 🏆 Recognition

Alle Beiträge werden im Projekt anerkannt:
- **Contributors** Sektion im README
- **Git Commit Attribution**
- **Release Notes** Erwähnung
- **GitHub Contributions** Graph

## 📞 Support & Questions

- **GitHub Discussions**: Allgemeine Fragen und Diskussionen
- **GitHub Issues**: Bugs und Feature Requests
- **Code Reviews**: PR Kommentare für technische Diskussionen

## 📄 License

Durch Beiträge zu diesem Projekt stimmen Sie zu, dass Ihre Beiträge unter der MIT-Lizenz lizenziert werden.

---

**Vielen Dank für Ihre Mitarbeit am DA-KI Projekt! 🚀**

*Entwickelt mit [Claude Code](https://claude.ai/code) - Moderne KI-gestützte Softwareentwicklung*