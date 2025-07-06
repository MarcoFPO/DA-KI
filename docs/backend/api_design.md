# Backend-API Design

Das Backend wird als REST-API mit FastAPI implementiert.

## 1. Authentifizierung
*   **Methode:** JSON Web Tokens (JWT).
*   **Umgebungsabhängig:**
    *   **Entwicklung:** Direkte Prüfung gegen `dev_secrets.json` (kein Hashing).
    *   **Produktion:** Prüfung gegen gehashte Passwörter in der Datenbank (Argon2/bcrypt).

## 2. Endpoint Design (Übersicht)
*   **Benutzerauthentifizierung:** `POST /token`, `POST /users/register`, `GET /users/me`.
*   **Aktienverwaltung:** `GET /stocks`, `POST /stocks`, `GET /stocks/{stock_id}`, `PUT /stocks/{stock_id}`, `DELETE /stocks/{stock_id}`.
*   **Analyse & Prognose:** `POST /analysis/start`.
*   **Aktienübernahme:** `POST /stocks/add_from_analysis`.
*   **Handelsfunktionen:** `POST /trade/buy`, `POST /trade/sell`.

## 3. Integration
Endpunkte nutzen Datenbank, ScoringEngine, EventScoringEngine, MLPredictor und Config-Klasse.

## 4. Fehlerbehandlung
Standardisierte HTTP-Statuscodes und JSON-Fehlerantworten.

## 5. Plugin-Management-API
*   **Endpunkte:** `GET /plugins` (Liste), `POST /plugins/{plugin_name}/activate`, `POST /plugins/{plugin_name}/deactivate`, `POST /plugins/reload`.
*   **Zugriffskontrolle:** Administratorrechte erforderlich.

## 6. Konfigurations-Management-API
*   **Endpunkte:** `GET /plugins/{plugin_name}/config/schema`, `GET /plugins/{plugin_name}/config`, `PUT /plugins/{plugin_name}/config`.
*   **Zugriffskontrolle:** Administratorrechte erforderlich.
