DA-KI Projektanforderungen
Projektziel
Privates Lernprojekt: Deutsche Aktienanalyse mit KI-Wachstumsprognose

Experimentieren mit verschiedenen Technologien
Praktische Erfahrung mit KI/ML in Finanzbereich sammeln
Infrastruktur-Skills (Linux, Proxmox, Netzwerktechnik) vertiefen
1. Lernziele und Funktionen
1.1 Technische Lernziele
 Python/Machine Learning: Pandas, NumPy, Scikit-learn, TensorFlow/PyTorch
 Datenverarbeitung: API-Integration, Datenbereinigung, Zeitreihenanalyse
 Web-Entwicklung: Flask/FastAPI, React/Vue.js, REST APIs
 Infrastruktur: Docker, Proxmox VMs/Container, nginx
 Datenbanken: PostgreSQL/MySQL, Redis für Caching
 DevOps: CI/CD, Monitoring, Logging
1.2 Kern-Features (MVP)
 Datensammlung: Kostenlose APIs (Yahoo Finance, Alpha Vantage Free Tier)
 Einfache Analyse: Grundlegende technische Indikatoren
 5-Faktor Scoring: Eigene Definition basierend auf verfügbaren Daten
 Einfaches Dashboard: Übersicht und Charts
 Experimentierbereich: Verschiedene ML-Modelle ausprobieren
1.3 Erweiterte Features (für später)
 Sentiment-Analyse von Nachrichten
 Portfolio-Tracking
 Backtesting von Strategien
 Erweiterte ML-Modelle (LSTM, Transformer)
2. Technischer Lern-Stack
2.1 Empfohlene Technologien (zum Lernen)
 Backend: Python + FastAPI (modern, async, gut dokumentiert)
 Frontend: React + TypeScript (weit verbreitet, gute Lernressourcen)
 Datenbank: PostgreSQL (robust, kostenlos, SQL-Skills)
 Cache: Redis (In-Memory, Sessions, API-Caching)
 ML: Scikit-learn → TensorFlow/PyTorch (Progression vom Einfachen zum Komplexen)
 Charts: Chart.js oder D3.js (Datenvisualisierung)
2.2 Infrastruktur-Lernziele
 Proxmox: LXC Container vs. VMs verstehen
 Docker: Multi-Stage Builds, Docker-Compose
 Reverse Proxy: nginx Konfiguration, SSL
 Monitoring: Prometheus + Grafana
 Networking: VLANs, Firewall-Regeln
2.3 Datenquellen (kostenlos/günstig)
 Yahoo Finance API (yfinance Python Library)
 Alpha Vantage (500 calls/Tag kostenlos)
 Financial Modeling Prep (250 calls/Tag kostenlos)
 Quandl/NASDAQ Data Link (begrenzte kostenlose Daten)
3. Lernstufen und Iterationen
3.1 Stufe 1: Grundlagen (2-3 Wochen)
 Lokale Entwicklung: Python Environment, erste API-Calls
 Datensammlung: Yahoo Finance Integration, CSV-Export
 Einfache Analyse: Moving Averages, RSI, MACD
 Erste Visualisierung: Matplotlib/Plotly Charts
3.2 Stufe 2: Web-Application (3-4 Wochen)
 FastAPI Backend: REST API für Aktiendaten
 React Frontend: Einfaches Dashboard
 PostgreSQL: Datenbank-Setup, Datenmodell
 Docker: Containerisierung der Komponenten
3.3 Stufe 3: Proxmox Deployment (2-3 Wochen)
 Container Setup: LXC Container für Services
 Networking: VLANs, Firewall-Konfiguration
 nginx: Reverse Proxy, SSL-Zertifikate
 Monitoring: Basis-Monitoring mit Grafana
3.4 Stufe 4: Machine Learning (4-6 Wochen)
 Datenaufbereitung: Feature Engineering
 ML-Modelle: Linear Regression → Random Forest → Neural Networks
 5-Faktor System: Eigene Scoring-Logik entwickeln
 Backtesting: Historische Performance prüfen
3.5 Stufe 5: Erweiterte Features (optional)
 Sentiment Analysis: News-Integration
 Real-time Updates: WebSockets
 Portfolio Management: Mehrere Aktien verwalten
 CI/CD Pipeline: Automatisierte Deployments
4. Einfaches 5-Faktor Scoring System (für Lernzwecke)
4.1 Faktor-Definition
Momentum (20%): Relative Strength Index (RSI), Price Change 3M
Trend (20%): Moving Average Convergence, Bollinger Bands Position
Volatilität (20%): Standard Deviation, Average True Range
Volumen (20%): Volume Trend, Volume Moving Average Ratio
Fundamental (20%): P/E Ratio, Dividend Yield (wenn verfügbar)
4.2 Scoring-Logik
Jeder Faktor: 0-20 Punkte
Gesamtscore: 0-100 Punkte
Kategorien: 80-100 (Stark), 60-79 (Gut), 40-59 (Neutral), 20-39 (Schwach), 0-19 (Sehr schwach)
5. Lern-Ressourcen und Tutorials
5.1 Python/Data Science
 Pandas: Offizielle Dokumentation + 10 Minutes to Pandas
 Scikit-learn: User Guide + Examples
 yfinance: GitHub Repository + Jupyter Notebooks
 FastAPI: Offizielle Tutorials (sehr gut!)
5.2 Frontend/Web
 React: Official Tutorial + Create React App
 TypeScript: TypeScript Handbook
 Chart.js: Getting Started Guide
5.3 Infrastructure
 Docker: Official Get Started Guide
 Proxmox: Community Wiki + YouTube Tutorials
 nginx: Beginner's Guide + SSL Configuration
5.4 Empfohlene Lernreihenfolge
Woche 1-2: Python + Pandas + API-Integration
Woche 3-4: FastAPI + REST APIs + PostgreSQL
Woche 5-6: React + Frontend Development
Woche 7-8: Docker + Proxmox Setup
Woche 9+: Machine Learning + Advanced Features
6. Erfolgs-Metriken für das Lernprojekt
6.1 Technische Meilensteine
 API-Integration: Erfolgreich Daten von Yahoo Finance abrufen
 Web-App: Funktionierendes Dashboard mit Charts
 Infrastruktur: Deployment auf Proxmox mit Docker
 ML-Modell: Erstes funktionierendes Prognose-Modell
 5-Faktor System: Eigene Scoring-Logik implementiert
6.2 Lern-Erfolge
 Python: Komfortabel mit Pandas, APIs, Web-Frameworks
 Frontend: Kann React-Apps erstellen und deployen
 DevOps: Versteht Docker, Proxmox, nginx-Konfiguration
 ML: Kann einfache Modelle trainieren und evaluieren
 Networking: Kann VLANs und Firewall-Regeln konfigurieren
7. Nächste Schritte
Sofort starten:
Development Environment: Python + IDE Setup
Erste API-Calls: yfinance installieren, DAX-Daten abrufen
Git Repository: Versionskontrolle einrichten
Jupyter Notebook: Erste Datenanalyse-Experimente
Diese Woche:
 Lokale Entwicklungsumgebung aufsetzen
 GitHub Repository für DA-KI erstellen
 Erste Aktiendaten abrufen und visualisieren
 Proxmox-Umgebung für späteres Deployment vorbereiten
Dieses Lernprojekt bietet praktische Erfahrung mit modernen Tech-Stacks und ist ein excellentes Portfolio-Projekt für Data Science, Web Development und DevOps Skills.

