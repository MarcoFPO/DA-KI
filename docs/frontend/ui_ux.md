# Frontend UI/UX

Das Frontend wird mit React und Material-UI (MUI) implementiert.

## 1. Projekt-Setup
Verwendung von `create-react-app` oder `Vite` für das initiale Scaffolding.

## 2. Komponenten-Design
Nutzung von Material-UI-Komponenten für konsistentes und wiederverwendbares UI-Design.

## 3. Routing
`react-router-dom` für Client-seitiges Routing.

## 4. Zustandsverwaltung
Initial React Context API oder `Zustand`.

## 5. API-Integration
`axios` oder `fetch` API für HTTP-Anfragen; JWT-basierte Authentifizierung.

## 6. Kernfunktionen der GUI
*   **Login- und Registrierungsseite:** Formulare für Benutzername/E-Mail und Passwort, Buttons für Login/Registrierung. JWT-Speicherung (Access Token in `localStorage`/`sessionStorage`, Refresh Token in HTTP-only Cookie für "Angemeldet bleiben").
*   **Dashboard / Portfolio-Übersicht (Dreigeteiltes Layout):**
    *   **Oberer Bereich:** Top 10 Aktien-Analysen (Liste, Details, "Zum Depot hinzufügen"-Button, "Analyse starten/aktualisieren"-Button).
    *   **Mittlerer Bereich:** Depot-Übersicht (Tabelle der verwalteten Aktien, Portfolio-Zusammenfassung, Aktions-Buttons).
    *   **Unterer Bereich:** Steuerfunktionen für Handel (Kaufen/Verkaufen) (Formulare für Kauf-/Verkaufsaufträge, Buttons, Cash-Bestand).
*   **Aktienverwaltung (Detailansicht / Bearbeiten):** Hinzufügen, Bearbeiten und Löschen von Aktien im Portfolio.
*   **Prognose-Start und Top-10-Anzeige:** Startet Analyse, zeigt Top-10-Ergebnisse, ermöglicht Übernahme.
*   **Admin-Bereich (Benutzerverwaltung):** Formular zum Hinzufügen neuer Benutzer.
*   **System-Status-Dashboard:** Zeigt Gesundheitszustand und Status der Backend-Module an.
*   **Globale Navigation:** Dropdown-Menü für den schnellen Wechsel zum Admin-Menü und System-Status-Dashboard (Zugriffskontrolle beachten).

## 7. Fehler- und Ladezustandsanzeige
*   **Ladeindikatoren:** `CircularProgress`, `LinearProgress`, `Skeleton` für visuelles Feedback bei Ladevorgängen.
    *   **Blinkende Anzeige bei API-Interaktion:** Ein kleines, nicht-invasives UI-Element, das kurz aufleuchtet/blinkt, sobald eine API-Anfrage gesendet wird, und wieder verschwindet, wenn die Antwort empfangen wurde. Dies erfordert einen globalen State, der die Anzahl der ausstehenden API-Anfragen verfolgt.
*   **Erfolgs-/Fehlermeldungen:** `Snackbar` für temporäre Nachrichten, `Alert` für prominentere Nachrichten.
*   **Validierungsfeedback:** Direkte Rückmeldung unter Eingabefeldern, visuelle Hervorhebung, Nutzung von Formular-Bibliotheken (z.B. `react-hook-form`).
