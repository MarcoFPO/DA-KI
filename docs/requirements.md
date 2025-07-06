# Anforderungskatalog für DA-KI

## 1. Einführung
DA-KI ist ein Projekt zur automatisierten Verwaltung eines Aktien-Depots.

## 2. Funktionale Anforderungen
Was das System tun soll. (z.B. "DA-KI soll X ermöglichen", "Benutzer sollen Y können")

### 2.1. Kernfunktionen
*   Kernfunktion 1: Analysieren der Aktien und erstellen einer Prognose der 10 Aktien mit der meisten Wertsteigerung (siehe [Datenquellen](data_sources.md), [Prognosemethodik](forecasting_methodology.md))
*   Kernfunktion 2: Verwaltung von ausgewählten Aktien
*   Kernfunktion 3: Regelmäßige Analyse der Aktien aus Kernfunktion 2 und daraus abgeleitete Funktionen für Kauf und Verkauf (Zugriff auf Onlinebroker via API für Kauf/Verkauf)
    *   **TODO:** Die genaue Broker-API (z.B. Bitpanda / One Trading) muss noch final evaluiert und spezifiziert werden. Die Machbarkeit des Aktienhandels über die anvisierte API ist zu prüfen.

### 2.2. Zusätzliche Funktionen
*   Web-GUI für die User-Bedienung
*   Möglichkeit, Kernfunktion 1 durch Userinteraktion zu starten
*   Möglichkeit, aus der Liste der Top-10-Aktien von Kernfunktion 1 eine Aktie in Kernfunktion 2 zu übernehmen
*   Admin-Menü zur Benutzerverwaltung (Hinzufügen von Benutzern, keine weitere Rechte-Differenzierung)
*   Ein System-Status-Dashboard, das den Zustand der einzelnen Module visualisiert. Dieses Dashboard wird von einem maschinenlesbaren API-Endpunkt gespeist, um eine automatisierte Auswertung (z.B. durch eine KI) zu ermöglichen.

## 3. Nicht-funktionale Anforderungen
Wie das System funktionieren soll.

### 3.1. Performance
*   **Asynchrone/Parallele Datenabfrage:** Die Datenbeschaffung von externen APIs durch die Filter- und Aggregations-Module muss asynchron und parallel erfolgen. Dies stellt sicher, dass Wartezeiten auf externe Dienste optimal genutzt werden und die Gesamtzeit für die Datenakquise minimiert wird.

### 3.2. Sicherheit und umgebungsspezifische Behandlung von Geheimnissen

**Wichtiger Hinweis zur Sicherheit:** Da das DA-KI-System ausschließlich in einem privaten Netzwerk betrieben wird und **nicht aus dem Internet erreichbar ist**, werden die Sicherheitsanforderungen entsprechend der Bedrohungslage angepasst. Die folgenden Sicherheitsmaßnahmen sind primär für eine eventuelle spätere Internetexposition vorgesehen.

Um die Sicherheit der Benutzerdaten zu gewährleisten und gleichzeitig eine effiziente Entwicklung zu ermöglichen, werden die Anforderungen je nach Betriebsumgebung (Produktion vs. Entwicklung) unterschieden.

**1. Benutzerauthentifizierung**
*   Ein sicheres Login-System (z.B. Benutzername/Passwort) ist erforderlich.
*   **Produktivumgebung:** Passwörter müssen zwingend mit einem modernen, starken Hashing-Algorithmus (z.B. Argon2 oder bcrypt) gesichert werden.
*   **Entwicklungsumgebung:** Für den einfachen Zugriff durch Entwickler und KI während der Entwicklung können Passwörter temporär in einer lokalen Konfigurationsdatei (`dev_secrets.json`) im Klartext gespeichert werden. Diese Datei **muss** in die `.gitignore`-Datei aufgenommen werden, um ein versehentliches Einchecken in die Versionskontrolle zu verhindern.

**2. Datentrennung**
*   Alle benutzerspezifischen Daten (Aktien-Portfolio, Handelshistorie) werden in der Datenbank fest mit der einzigartigen ID des jeweiligen Benutzers verknüpft.
*   Die Anwendungslogik muss auf allen Ebenen sicherstellen, dass ein eingeloggter Benutzer ausschließlich auf die Daten zugreifen kann, die mit seiner eigenen Benutzer-ID verknüpft sind.

**3. Speicherung von API-Schlüsseln**
*   **Produktivumgebung:** Broker-API-Schlüssel werden in der Datenbank mit einem starken symmetrischen Algorithmus (z.B. AES-256-GCM) verschlüsselt. Der Haupt-Schlüssel zur Ver- und Entschlüsselung (`master key`) wird **erst nach der finalen Abnahme manuell auf dem Zielsystem** an einer sicheren Stelle (z.B. als Umgebungsvariable oder in einem Secret-Management-Tool) hinterlegt. Er darf unter keinen Umständen im Quellcode gespeichert werden.
*   **Entwicklungsumgebung:** Die API-Schlüssel werden für den einfachen Zugriff ebenfalls in der `dev_secrets.json`-Datei im Klartext gespeichert. Die Anwendung greift im Entwicklungsmodus direkt auf diese Datei zu.

**4. Sichere Kommunikation (TLS/SSL)**
*   **Zertifikatsbeschaffung:** Verwendung von Let's Encrypt für kostenlose, automatisierte TLS/SSL-Zertifikate.
*   **Webserver / Reverse Proxy:** Einsatz von Nginx als Reverse Proxy für TLS-Terminierung, Port-Weiterleitung (HTTP auf HTTPS) und Proxying an die interne Anwendung.
*   **TLS-Konfigurations-Best Practices:** Nur TLS 1.2 und TLS 1.3 zulassen, Verwendung von modernen, sicheren Cipher Suiten, korrekte Bereitstellung der Zertifikatskette.

### 3.3. Benutzerfreundlichkeit (Usability)
*   **UI-Framework:** React mit Material-UI (MUI) für ein konsistentes und modernes Erscheinungsbild.
*   **Feedback-Mechanismen:** Implementierung klarer visueller und textueller Rückmeldungen für Benutzeraktionen (z.B. Ladeindikatoren, Erfolgs-/Fehlermeldungen, Validierungsfeedback). Die Feedback-Funktion selbst wird nicht benötigt.

### 3.4. Skalierbarkeit
*   **Horizontale Skalierung:** Das System wird als monolithische Anwendung innerhalb eines einzelnen LXC-Containers betrieben. Skalierung erfolgt durch Erhöhung der Ressourcen des Containers (vertikale Skalierung).
*   **Datenwachstum:** Für 2-5 Benutzer, die jeweils 10-20 Aktien mit mindestens 10 Jahren historischen Daten verwalten, ist SQLite als lokale Kandidaten-Datenbank ausreichend. Der geschätzte Speicherbedarf liegt im MB-Bereich.
*   **Ressourcen-Management im LXC-Container:** Initiale Zuweisung von 2 CPU-Kernen, 4 GB RAM und 20 GB Festplattenspeicher. Ressourcen können bei Bedarf dynamisch angepasst werden.

### 3.5. Wartbarkeit
*   **Code-Standards:**
    *   **Python:** PEP 8, automatische Formatierung mit Black, Linting mit Ruff.
    *   **JavaScript/React:** Linting mit ESLint (z.B. `eslint-config-airbnb`), automatische Formatierung mit Prettier.
*   **Dokumentation:**
    *   **Code-Dokumentation:** Docstrings im Google- oder Sphinx-Stil für Python, JSDoc-Kommentare für JavaScript/React.
    *   **Architektur-Dokumentation:** C4-Modell für Diagramme, umfassende `README.md`, detaillierte Dokumentation im `docs/` Verzeichnis.
*   **Testabdeckung:**
    *   **Unit-Tests:** Ziel von >90% Code-Coverage für kritische Geschäftslogik (Python: `pytest`; JavaScript/React: `Jest`, `React Testing Library`).
    *   **Integrationstests:** Für Modulinteraktionen und externe API-Aufrufe (mit Mocks).
    *   **End-to-End-Tests:** Für die wichtigsten Benutzerpfade in der Web-GUI (z.B. mit Cypress oder Playwright).
*   **Abhängigkeitsmanagement:**
    *   **Python:** Poetry für Paketverwaltung und reproduzierbare Umgebungen.
    *   **JavaScript/React:** npm oder Yarn.
    *   Regelmäßige Überprüfung und Aktualisierung von Abhängigkeiten.

### 3.6. Deployment- und Entwicklungsumgebung
*   Das System soll in einem LXC-Container mit aktuellem Debian betrieben werden.
*   Dieser LXC-Container dient sowohl als **Entwicklungsumgebung** als auch als **Zielsystem** für den Produktivbetrieb.

### 3.7. Datenarchitektur und -speicherung

Um die Effizienz zu maximieren und die Datenspeicherung platzsparend und überschaubar zu halten, wird eine dreistufige Datenarchitektur verfolgt:

1.  **Stufe 1: Dezentrale Filter- und Aggregations-Modules**
    *   Für jede externe Datenquelle (z.B. Alpha Vantage, FRED) wird ein eigenständiges Modul entwickelt.
    *   Dieses Modul filtert die Daten seiner Quelle nach vordefinierten Kriterien, um eine Vorauswahl vielversprechender Aktien (Kandidaten) zu treffen.
    *   Für jeden identifizierten Kandidaten ist das Modul dafür verantwortlich, **alle für die spätere Analyse benötigten Kennzahlen und Zeitreihen** zu sammeln und zu aggregieren.
    *   **Fehlerbehandlung:** Sollte ein Modul nicht alle für eine vollständige Analyse erforderlichen Datenpunkte ermitteln können, **muss dieser Datensatz in der Datenbank explizit als "unvollständig" markiert werden.**

2.  **Stufe 2: Lokale Kandidaten-Datenbank**
    *   Als Datenbanktechnologie wird **SQLite** verwendet. Dies ist ressourcenschonend und erfordert keinen separaten Datenbankserver.
    *   Die Filter-Module speichern die vollständigen, in sich geschlossenen Datensätze der Kandidaten in dieser lokalen Datenbank ab. Jeder Datensatz enthält den Ticker, den Grund der Auswahl, den Zeitstempel, alle aggregierten Datenpunkte sowie die Markierung, ob der Datensatz vollständig ist.

3.  **Stufe 3: Haupt-Analyse-Engine**
    *   Die rechenintensive Hauptanalyse (Scoring und Machine Learning) arbeitet **ausschließlich** auf den Daten in der lokalen SQLite-Datenbank. Es finden während der Analyse keine externen API-Aufrufe statt.
    *   **Fehlertoleranz:** Die Haupt-Analyse-Engine **muss fehlertolerant implementiert werden.** Sie muss in der Lage sein, Datensätze, die als "unvollständig" markiert sind, zu erkennen und angemessen zu behandeln (z.B. durch Überspringen des Kandidaten oder durch eine nur teilweise durchgeführte Analyse), ohne dass der Gesamtprozess fehlschlägt.

### 3.8. Monitoring und Systemintegrität

Um die Zuverlässigkeit, Wartbarkeit und automatisierte Analyse des Systems zu gewährleisten, werden folgende Anforderungen an das Monitoring gestellt:

*   **Modul-Status:** Jedes unabhängige Modul (z.B. Daten-Filter, Analyse-Engine) muss seinen eigenen Betriebszustand überwachen und detailliert protokollieren.

*   **Handshake-Prinzip zur Datenübergabe:** Die Übergabe von Daten zwischen den Modulen oder in die Datenbank muss nach einem Handshake-Prinzip erfolgen. Die erfolgreiche Bestätigung der Datenannahme muss im Status des sendenden Moduls vermerkt werden.

*   **Maschinenlesbarer Status-Endpunkt:** Die gesammelten Status-Informationen aller Module müssen über einen dedizierten API-Endpunkt in einem **strukturierten, maschinenlesbaren Format (z.B. JSON)** bereitgestellt werden. Die Datenstruktur muss konsistent und wohldefiniert sein, um eine programmatische Auswertung durch externe Tools oder eine KI zu ermöglichen.

*   **Visuelles Dashboard:** Das unter "Zusätzliche Funktionen" definierte System-Status-Dashboard konsumiert die Daten dieses API-Endpunkts, um eine für Menschen leicht verständliche, visuelle Übersicht des Systemzustands zu bieten.

*   **Alerting:** Definition von Schwellenwerten für Metriken, bei deren Überschreitung Alarme ausgelöst werden sollen (z.B. API-Fehlerquote > 5%, keine neuen Datenpunkte seit X Stunden, Latenz des Prognose-API-Endpunkts > 2 Sekunden, Speichernutzung > 90%, Festplattenspeicher < 10%). Die Alert-Informationen werden über den maschinenlesbaren Status-Endpunkt bereitgestellt und vom visuellen System-Status-Dashboard auf der GUI konsumiert und angezeigt.

*   **Log-Management:**
    *   **Strukturierte Logs:** Alle Logs sollten in einem strukturierten Format (z.B. JSON) ausgegeben werden, um eine einfache Parsbarkeit und Analyse zu ermöglichen.
    *   **Log-Level:** Konsistente Verwendung von Log-Levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).

*   **Health Checks:**
    *   **Liveness Probes:** Ein einfacher HTTP-Endpunkt (z.B. `/health/liveness`), der einen 200 OK-Status zurückgibt, solange der Anwendungsprozess aktiv ist.
    *   **Readiness Probes:** Ein HTTP-Endpunkt (z.B. `/health/readiness`), der einen 200 OK-Status nur dann zurückgibt, wenn die Anwendung vollständig initialisiert ist und alle kritischen externen Abhängigkeiten funktionieren.

### 3.9. Systemarchitektur: Plugin-basiert

Um maximale Modularität, Erweiterbarkeit und Wartbarkeit zu gewährleisten, wird die Systemarchitektur auf einem dynamischen Plugin-Konzept aufgebaut.

*   **Plugin-Architektur für Datenquellen:** Die dezentralen Filter-Module werden als eigenständige Plugins implementiert.
    *   Es wird ein zentrales Plugin-Verzeichnis (`src/data_source_plugins/`) angelegt.
    *   Für jedes Plugin muss eine einheitliche, vorgegebene Programmierschnittstelle (ein "Interface" oder eine "abstrakte Basisklasse") implementiert werden. Diese Schnittstelle definiert die Methoden, die jedes Plugin bereitstellen muss (z.B. `fetch_candidates`).

*   **Dynamisches Laden zur Laufzeit:** Das System muss in der Lage sein, neue Plugins, die dem Plugin-Verzeichnis hinzugefügt werden, **zur Laufzeit** zu erkennen und zu laden, ohne dass ein Neustart der Hauptanwendung erforderlich ist. Ein dedizierter API-Endpunkt soll das Neuladen der Plugins auslösen.

*   **Verwaltung über das Web-Frontend:** Die Verwaltung der Plugins erfolgt über das System-Status-Dashboard.
    *   Der Zustand jedes Plugins (z.B. geladen, aktiv, inaktiv, Fehler) muss über den maschinenlesbaren Status-API-Endpunkt abrufbar sein.
    *   Die API muss ebenfalls Endpunkte bereitstellen, um Plugins gezielt zu **aktivieren, zu deaktivieren oder neu zu laden**.
    *   Das Web-Frontend dient als grafische Benutzeroberfläche, um diese Verwaltungsfunktionen komfortabel zu nutzen.

### 3.10. Zentrales Konfigurations-Management

Alle nicht-sensiblen, umgebungsspezifischen oder einstellbaren Parameter des Systems müssen in einer zentralen Konfigurationsstruktur verwaltet werden.

*   **Globale Konfiguration:** Eine Haupt-Konfigurationsdatei (`config.yaml`) enthält globale Parameter, die keine Geheimnisse sind (z.B. Standard-Timeouts, allgemeine Systempfade). Diese Datei wird Teil der Versionskontrolle sein.

*   **Plugin-spezifische Konfiguration:** Jedes dynamisch ladbare Plugin-Modul (siehe 3.9) muss eine eigene Konfigurationsdatei besitzen.
    *   Diese Dateien werden im jeweiligen Plugin-Verzeichnis abgelegt (z.B. `src/data_source_plugins/alpha_vantage/config.yaml`).
    *   Sie enthalten alle spezifischen Parameter für das jeweilige Plugin (z.B. Schwellenwerte für Indikatoren, spezifische API-URLs).
    *   **Standardwerte (Defaults):** Für jeden konfigurierbaren Wert muss ein Standardwert (Default) definiert werden. Diese Standardwerte werden im Zuge der Entwicklung festgelegt.
    *   **Web-basierte Editierbarkeit:** Diese Plugin-Konfigurationsdateien müssen über das Web System-Status-Dashboard (siehe 2.2) editierbar sein. Dies erfordert entsprechende API-Endpunkte, die das Lesen und Schreiben dieser Konfigurationen ermöglichen.
    *   **Parameter-Beschreibungen:** Für jeden konfigurierbaren Wert muss eine kurze, verständliche Beschreibung hinterlegt werden, die **auch den Standardwert klar ersichtlich macht**. Diese Beschreibungen werden im Web-Frontend angezeigt, um die Bedienung zu erleichtern. Die technische Umsetzung dieser Beschreibung (z.B. als Metadaten im Konfigurationsformat oder über ein separates Schema) ist bei der Implementierung zu klären.



## 4. Benutzerrollen
Alle Benutzer haben die gleichen Rechte und Zugriff auf alle Funktionen. Es gibt keine differenzierten Benutzerrollen.

## 5. Einschränkungen
Welche Grenzen oder Bedingungen gibt es für das Projekt?

*   Für Netzwerk-Verbindungen dürfen "localhost" und "127.0.0.0/8" nicht verwendet werden.
*   Es soll immer der Port 443 für Verbindungen genutzt werden.
*   Port 80 soll eine Weiterleitung auf Port 443 erhalten.
*   Der Aufruf der Anwendung soll über eine vollständige Domain oder die IP-Adresse des Servers erfolgen, ohne Subverzeichnisse nutzen zu müssen.
