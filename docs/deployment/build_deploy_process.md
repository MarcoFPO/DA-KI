# Build- und Deployment-Prozess

Dieses Dokument beschreibt die Schritte für den Build- und Deployment-Prozess der DA-KI-Anwendung.

## 1. Setup-Skript
Ein `setup.sh`-Skript wird verwendet, um die notwendigen Systemabhängigkeiten (z.B. `git`, `nodejs`, `nginx`, `certbot`), die Python-Umgebung (Poetry) und Node.js auf einem minimalen Debian LXC-Container zu installieren. Alle Pakete werden in der möglichst neuesten Version installiert.

## 2. Build-Prozess
*   **Backend (Python):** Nach dem Klonen des Repositorys werden die Python-Abhängigkeiten mit `poetry install` im Projektverzeichnis installiert.
*   **Frontend (React):** Das Frontend wird in statische Dateien kompiliert und optimiert. Dies erfolgt durch Navigieren in das Frontend-Projektverzeichnis, Installation der JavaScript-Abhängigkeiten (`npm install` oder `yarn install`) und Ausführung des Build-Befehls (`npm run build` oder `yarn build`). Die optimierten Dateien werden im `build/` (oder `dist/`) Verzeichnis abgelegt.

## 3. Start-Skript (systemd Services)
Die Anwendungskomponenten werden als `systemd` Services konfiguriert, um einen automatischen Start beim Systemboot, Hintergrundausführung und Überwachung/Neustart im Fehlerfall zu gewährleisten.

*   **Backend Service:** Eine `systemd` Service-Datei (z.B. `/etc/systemd/system/daki-backend.service`) wird erstellt, um die Python-Backend-Anwendung (Uvicorn) zu starten. Beispiel `ExecStart`: `/home/mdoehler/.poetry/bin/poetry run uvicorn main:app --host YOUR_LXC_CONTAINER_IP --port 8000` (wobei `YOUR_LXC_CONTAINER_IP` die feste IP-Adresse des Containers ist).
*   **Frontend Service:** Da das React-Frontend als statische Dateien von Nginx ausgeliefert wird, ist kein separater `systemd` Service für das Frontend erforderlich.

## 4. Nginx-Konfiguration
Nginx wird als Reverse Proxy für das Backend und zur Auslieferung der statischen Frontend-Dateien konfiguriert. Es übernimmt die TLS-Terminierung und leitet HTTP-Anfragen auf HTTPS um.

*   **Backend-Proxying:** Anfragen an die API (z.B. `/api/v1/`) werden an die spezifische IP-Adresse des LXC-Containers und den internen Port des Backend-Servers weitergeleitet (z.B. `http://YOUR_LXC_CONTAINER_IP:8000`).
*   **Frontend-Auslieferung:** Statische Dateien des React-Frontends werden direkt von Nginx ausgeliefert.
*   **TLS/SSL:** Let's Encrypt-Zertifikate werden mit Certbot beantragt und die Nginx-Konfiguration automatisch für HTTPS angepasst. Ein Cronjob wird für die automatische Zertifikatserneuerung eingerichtet.
