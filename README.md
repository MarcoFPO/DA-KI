# DA-KI - Deutsche Aktienanalyse mit KI

🚀 **Privates Lernprojekt für deutsche Aktienanalyse mit KI-Wachstumsprognose**

## Projekt-Übersicht

DA-KI ist eine intelligente Fintech-Plattform, die als Lernprojekt entwickelt wird, um praktische Erfahrungen mit modernen Technologien zu sammeln:

- **Backend**: Python FastAPI mit PostgreSQL
- **Frontend**: React mit TypeScript
- **Infrastructure**: LXC Container auf Proxmox
- **ML/AI**: Scikit-learn für 5-Faktor Scoring System
- **Deployment**: Debian-basiert mit deutscher Lokalisierung

## Lernziele

- 🐍 **Python Development**: FastAPI, Pandas, Machine Learning
- 🌐 **Web Development**: React, REST APIs, Datenvisualisierung
- 🏗️ **Infrastructure**: LXC Container, nginx, PostgreSQL, Redis
- 🤖 **Machine Learning**: Finanzanalyse, Prognosemodelle
- 🔧 **DevOps**: Systemd, Supervisor, Monitoring

## Quick Start

### 1. LXC Container erstellen
```bash
# Debian 12 Container mit IP 10.1.1.110/24
# Siehe: docs/03-installation/01-basis-setup.md
```

### 2. Basis-Installation
```bash
git clone https://github.com/MarcoFPO/DA-KI.git
cd DA-KI
chmod +x scripts/setup/install-base.sh
./scripts/setup/install-base.sh
```

### 3. Services konfigurieren
```bash
./scripts/setup/configure-services.sh
```

### 4. Test-API starten
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 10.1.1.110 --port 8000
```

## Architektur

```
┌─────────────────────────────────────┐
│ LXC Container (10.1.1.110)         │
├─────────────────────────────────────┤
│ nginx (Port 80) → React Frontend    │
│ FastAPI (Port 8000) → Python Backend│
│ PostgreSQL (Port 5432) → Database   │
│ Redis (Port 6379) → Cache           │
└─────────────────────────────────────┘
```

## 5-Faktor Scoring System

1. **Momentum (20%)**: RSI, Price Change 3M
2. **Trend (20%)**: Moving Average, Bollinger Bands
3. **Volatilität (20%)**: Standard Deviation, ATR
4. **Volumen (20%)**: Volume Trend, MA Ratio
5. **Fundamental (20%)**: P/E Ratio, Dividend Yield

## Dokumentation

- 📋 [Projektanforderungen](docs/01-projektanforderungen.md)
- 🏗️ [Umgebungsplanung](docs/02-umgebungsplanung.md)
- 🔧 [Installation](docs/03-installation/)
- 💻 [Entwicklung](docs/04-entwicklung/)
- 🚀 [Deployment](docs/05-deployment/)

## Technischer Stack

### Backend
- **Python 3.11+** mit FastAPI
- **PostgreSQL 15+** für Datenspeicherung
- **Redis** für Caching
- **pandas/numpy** für Datenverarbeitung
- **yfinance** für Aktiendaten
- **scikit-learn** für ML-Modelle

### Frontend
- **React 18+** mit TypeScript
- **Chart.js** für Datenvisualisierung
- **Tailwind CSS** für Styling

### Infrastructure
- **Debian 12** LXC Container
- **nginx** als Reverse Proxy
- **Supervisor** für Process Management
- **systemd** für Service Management

## Entwicklungsumgebung

### Lokale Entwicklung
```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
npm start
```

### Container-Entwicklung
```bash
# SSH in Container
ssh root@10.1.1.110

# Services prüfen
systemctl status daki-api
supervisorctl status
```

## API-Endpoints

- `GET /` - Willkommensnachricht
- `GET /health` - Gesundheitsstatus
- `GET /api/stocks` - Aktienliste
- `GET /api/stocks/{symbol}` - Aktiendetails
- `GET /api/analysis/{symbol}` - 5-Faktor Analyse

## Lizenz

Dieses Projekt ist für Lernzwecke entwickelt und unter der MIT-Lizenz veröffentlicht.

## Beitragen

Da dies ein privates Lernprojekt ist, sind Pull Requests willkommen, besonders für:
- Verbesserungen der ML-Algorithmen
- Frontend-Optimierungen
- Dokumentation
- Bug-Fixes

## Kontakt

- **Autor**: Marco
- **GitHub**: https://github.com/MarcoFPO
- **Projekt**: Lernprojekt für deutsche Aktienanalyse

---

⚠️ **Disclaimer**: Dieses Projekt dient nur Lernzwecken. Keine Anlageberatung!
