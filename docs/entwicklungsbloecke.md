### Entwicklungsblöcke für DA-KI

Diese Liste unterteilt die Entwicklungsarbeit für das DA-KI-Projekt in überschaubare Blöcke, die relativ unabhängig voneinander bearbeitet werden können.

---

**Block A: Kern-Infrastruktur (Fundament)**
*   **Beschreibung:** Bereitstellung der grundlegenden Projektstruktur, Datenbank und des Geheimnismanagements.
*   **Abhängigkeiten:** Keine (Startpunkt).
*   **Aufgaben:**
    *   A1: Projekt-Scaffolding (Verzeichnisstruktur, Git-Repo).
    *   A2: Datenbank-Setup (SQLite-Schema für `candidates`, `historical_data`, `users`, `portfolios`, `transactions` und `db_setup.py` Skript).
    *   A3: Geheimnismanagement (`Config`-Klasse, `dev_secrets.json` Struktur, Passwort-Hashing-Funktionen, API-Schlüssel-Verschlüsselungsfunktionen).
    *   A4: Plugin-Infrastruktur (Abstrakte `DataSourcePlugin`-Klasse, `PluginManager` für dynamisches Laden und Registrierung).

**Block B: Backend-Kernlogik (Berechnungen)**
*   **Beschreibung:** Implementierung der Kernberechnungsmodule, die unabhängig von der API oder dem Frontend funktionieren.
*   **Abhängigkeiten:** Block A (für Datenbankzugriff, Geheimnisse).
*   **Aufgaben:**
    *   B1: Technische Indikatoren Bibliothek (`src/technical_indicators/` mit Funktionen zur Berechnung von RSI, MACD, EMA, Bollinger Bands etc.).
    *   B2: `ScoringEngine` (Implementierung der Scoring-Logik für alle technischen Indikatoren).
    *   B3: `EventScoringEngine` (Implementierung der Event-Scoring-Logik).
    *   B4: `ML Data Preparation` (Klasse zur Vorbereitung von Features und Zielvariablen für ML-Modelle).
    *   B5: `ML Predictor` (Klasse für Modelltraining, Speicherung und Vorhersage, inkl. Online Learning-Fähigkeit).

**Block C: Backend-API (Schnittstelle zur Welt)**
*   **Beschreibung:** Bereitstellung der REST-API-Endpunkte, die die Backend-Kernlogik exponieren.
*   **Abhängigkeiten:** Block A (für Authentifizierung, Geheimnisse), Block B (für Scoring, ML-Vorhersagen).
*   **Aufgaben:**
    *   C1: FastAPI-Setup und grundlegende Authentifizierung (JWT, Login/Registrierung Endpunkte).
    *   C2: Benutzerverwaltung API-Endpunkte (`/users`).
    *   C3: Aktienverwaltung API-Endpunkte (`/stocks`).
    *   C4: Analyse- und Prognose-API-Endpunkte (`/analysis/start`, `/stocks/add_from_analysis`).
    *   C5: Handelsfunktionen API-Endpunkte (`/trade/buy`, `/trade/sell`).
    *   C6: System-Status-API-Endpunkt (`/status`).
    *   C7: Plugin-Management-API-Endpunkte (`/plugins`).
    *   C8: Konfigurations-Management-API-Endpunkte (`/plugins/{plugin_name}/config`).

**Block D: Frontend-Grundlagen (UI-Shell)**
*   **Beschreibung:** Aufbau der grundlegenden Frontend-Struktur und der UI-Komponenten.
*   **Abhängigkeiten:** Block C (für API-Interaktion).
*   **Aufgaben:**
    *   D1: React-Projekt-Setup (Vite/CRA, Material-UI).
    *   D2: Routing (`react-router-dom`).
    *   D3: Globale Zustandsverwaltung (React Context API / Zustand für Auth-Status, Ladezustände).
    *   D4: API-Integration Layer (`axios`/`fetch`, JWT-Handling, globale Ladeanzeige mit Blinken).
    *   D5: Fehler- und Ladezustandsanzeige (Snackbar, Alert, Validierungsfeedback).

**Block E: Frontend-Funktionen (Benutzerinteraktion)**
*   **Beschreibung:** Implementierung der spezifischen Benutzeroberflächen für die Kernfunktionen.
*   **Abhängigkeiten:** Block D (für UI-Grundlagen, API-Integration).
*   **Aufgaben:**
    *   E1: Login- und Registrierungsseite UI.
    *   E2: Dashboard UI (dreigeteilt: Top 10, Depot, Handelsfunktionen).
    *   E3: Aktienverwaltung UI (Detailansicht, Bearbeiten, Hinzufügen/Löschen).
    *   E4: Prognose-Start und Top-10-Anzeige UI.
    *   E5: Admin-Bereich UI (Benutzerverwaltung).
    *   E6: System-Status-Dashboard UI.
    *   E7: Globale Navigation (Dropdowns für Admin/Status).

**Block F: Deployment & Betrieb (Produktionsreife)**
*   **Beschreibung:** Vorbereitung der Anwendung für den Produktivbetrieb und die Überwachung.
*   **Abhängigkeiten:** Block A, B, C, D, E (für die vollständige Anwendung).
*   **Aufgaben:**
    *   F1: Server-Vorbereitung (`prepare_server.sh` Skript).
    *   F2: Build-Prozess (Backend Poetry, Frontend React Build).
    *   F3: `systemd` Service-Dateien für Backend.
    *   F4: Nginx-Konfiguration (Finalisierung, SSL mit Certbot).
    *   F5: Implementierung detaillierter Logging-Mechanismen im Code.
    *   F6: Health Check Endpunkte (`/health/liveness`, `/health/readiness`).
