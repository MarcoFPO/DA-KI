# Bereitstellungsanleitung für DA-KI

Diese Anleitung beschreibt die sequenziellen Schritte zur Vorbereitung des Servers und zur Bereitstellung der DA-KI-Anwendung.

**Wichtiger Hinweis:** Ersetzen Sie alle Platzhalter wie `your_domain.com`, `YOUR_LXC_CONTAINER_IPV4`, `YOUR_LXC_CONTAINER_IPV6` und Pfade durch Ihre tatsächlichen Werte.

---

### Schritt-für-Schritt-Anleitung zur DA-KI Server- und Anwendungsbereitstellung

**Voraussetzung:** Ein frisch installierter, minimaler Debian LXC-Container mit fester IPv4- und IPv6-Adresse. SSH-Zugriff auf den Container ist konfiguriert.

**1. Server-Vorbereitung (Ausführung des `prepare_server.sh` Skripts)**

*   **Zweck:** Installiert alle notwendigen Systempakete, Entwicklungstools, Poetry, Node.js, Nginx und Certbot. Konfiguriert den SSH-Server und bereitet die Nginx-Konfiguration vor.
*   **Befehle:**
    1.  Kopieren Sie das Skript `prepare_server.sh` (das wir in `/home/mdoehler/DA-KI/docs/prepare_server.sh` gespeichert haben) auf Ihren LXC-Container, z.B. in Ihr Home-Verzeichnis.
        ```bash
        # Beispiel: Vom lokalen Rechner aus
        scp /home/mdoehler/DA-KI/docs/prepare_server.sh user@your_lxc_ip:/home/user/
        ```
    2.  Verbinden Sie sich per SSH mit Ihrem LXC-Container.
        ```bash
        ssh user@your_lxc_ip
        ```
    3.  Machen Sie das Skript ausführbar:
        ```bash
        chmod +x prepare_server.sh
        ```
    4.  Führen Sie das Skript aus:
        ```bash
        sudo ./prepare_server.sh
        ```
    *   **Aktion nach Ausführung:** Das Skript wird die Installationen durchführen und Nginx initial konfigurieren. Es wird Sie daran erinnern, die Platzhalter in der Nginx-Konfiguration zu ersetzen.

**2. DA-KI Anwendungs-Code klonen**

*   **Zweck:** Den Quellcode der DA-KI-Anwendung auf den Server bringen.
*   **Befehle:**
    1.  Navigieren Sie zum Home-Verzeichnis des Benutzers (oder dem gewünschten Installationspfad).
    2.  Klonen Sie Ihr DA-KI Git-Repository:
        ```bash
        git clone your_daki_repository_url /home/mdoehler/DA-KI/
        ```

**3. Nginx Konfiguration anpassen**

*   **Zweck:** Die Nginx-Konfiguration mit Ihren tatsächlichen Domain- und IP-Informationen aktualisieren.
*   **Befehle:**
    1.  Öffnen Sie die Nginx-Konfigurationsdatei:
        ```bash
        sudo nano /etc/nginx/sites-available/daki-app.conf
        ```
    2.  Ersetzen Sie die Platzhalter `your_domain.com`, `YOUR_LXC_CONTAINER_IPV4`, `YOUR_LXC_CONTAINER_IPV6` durch Ihre tatsächlichen Werte.
    3.  Speichern und schließen Sie die Datei.
    4.  Testen Sie die Nginx-Konfiguration und laden Sie sie neu:
        ```bash
        sudo nginx -t && sudo systemctl reload nginx
        ```

**4. TLS/SSL-Zertifikate mit Certbot beantragen**

*   **Zweck:** Kostenlose Let's Encrypt SSL-Zertifikate erhalten und Nginx für HTTPS konfigurieren.
*   **Befehle:**
    1.  Führen Sie Certbot aus. Stellen Sie sicher, dass Ihre Domain bereits auf die IP-Adresse Ihres Servers zeigt.
        ```bash
        sudo certbot --nginx -d your_domain.com
        ```
    *   **Aktion nach Ausführung:** Certbot wird Sie durch den Prozess führen, die Zertifikate erhalten und die Nginx-Konfiguration automatisch für HTTPS anpassen (einschließlich der HTTP-zu-HTTPS-Weiterleitung).

**5. Datenbank-Setup (SQLite)**

*   **Zweck:** Die SQLite-Datenbankdatei erstellen und das Schema initialisieren.
*   **Befehle:**
    1.  Navigieren Sie zum Datenbank-Setup-Skript:
        ```bash
        cd /home/mdoehler/DA-KI/src/database/
        ```
    2.  Führen Sie das Skript aus:
        ```bash
        python3 db_setup.py
        ```
    *   **Aktion nach Ausführung:** Eine `daki.db`-Datei wird im Verzeichnis `/home/mdoehler/DA-KI/data/` erstellt und die Tabellen (`candidates`, `historical_data`, `users`, `portfolios`, `transactions`) werden initialisiert.

**6. Backend Build-Prozess (Poetry Abhängigkeiten installieren)**

*   **Zweck:** Die Python-Abhängigkeiten des Backend-Projekts installieren.
*   **Befehle:**
    1.  Navigieren Sie zum Backend-Verzeichnis:
        ```bash
        cd /home/mdoehler/DA-KI/backend/ # Beispielpfad
        ```
    2.  Installieren Sie die Abhängigkeiten mit Poetry:
        ```bash
        poetry install
        ```

**7. Frontend Build-Prozess (React kompilieren)**

*   **Zweck:** Das React-Frontend in statische Dateien kompilieren und optimieren.
*   **Befehle:**
    1.  Navigieren Sie zum Frontend-Verzeichnis:
        ```bash
        cd /home/mdoehler/DA-KI/frontend/ # Beispielpfad
        ```
    2.  Installieren Sie die JavaScript-Abhängigkeiten:
        ```bash
        npm install # oder yarn install
        ```
    3.  Führen Sie den Build-Befehl aus:
        ```bash
        npm run build # oder yarn build
        ```
    *   **Aktion nach Ausführung:** Ein `build/` (oder `dist/`) Verzeichnis wird mit den optimierten statischen Frontend-Dateien erstellt.

**8. Nginx Konfiguration für Frontend-Auslieferung anpassen**

*   **Zweck:** Nginx anweisen, die statischen Dateien des gebauten Frontends auszuliefern.
*   **Befehle:**
    1.  Öffnen Sie die Nginx-Konfigurationsdatei erneut:
        ```bash
        sudo nano /etc/nginx/sites-available/daki-app.conf
        ```
    2.  Suchen Sie den `location /` Block im `server` Block für Port 443 und ersetzen Sie den Platzhalter `return 200` durch die tatsächlichen `root` und `try_files` Direktiven:
        ```nginx
        location / {
            root /home/mdoehler/DA-KI/frontend/build; # Pfad zum React-Build-Verzeichnis
            index index.html index.htm;
            try_files \$uri \$uri/ /index.html; # Für React SPA Routing
        }
        ```
    3.  Speichern und schließen Sie die Datei.
    4.  Testen Sie die Nginx-Konfiguration und laden Sie sie neu:
        ```bash
        sudo nginx -t && sudo systemctl reload nginx
        ```

**9. Backend als `systemd` Service einrichten und starten**

*   **Zweck:** Sicherstellen, dass das Backend automatisch startet und überwacht wird.
*   **Befehle:**
    1.  Erstellen Sie die `systemd` Service-Datei:
        ```bash
        sudo nano /etc/systemd/system/daki-backend.service
        ```
    2.  Fügen Sie den Inhalt der Service-Datei ein (ersetzen Sie `YOUR_LXC_CONTAINER_IP` durch die tatsächliche IP):
        ```ini
        [Unit]
        Description=DA-KI Backend Application
        After=network.target

        [Service]
        User=mdoehler # Oder der Benutzer, unter dem die Anwendung laufen soll
        Group=mdoehler # Oder die Gruppe
        WorkingDirectory=/home/mdoehler/DA-KI/backend # Pfad zum Backend-Verzeichnis
        ExecStart=/home/mdoehler/.poetry/bin/poetry run uvicorn main:app --host YOUR_LXC_CONTAINER_IP --port 8000
        Restart=always
        RestartSec=5
        StandardOutput=journal
        StandardError=journal

        [Install]
        WantedBy=multi-user.target
        ```
    3.  Speichern und schließen Sie die Datei.
    4.  Laden Sie `systemd` neu:
        ```bash
        sudo systemctl daemon-reload
        ```
    5.  Aktivieren Sie den Service für den automatischen Start:
        ```bash
        sudo systemctl enable daki-backend.service
        ```
    6.  Starten Sie den Service:
        ```bash
        sudo systemctl start daki-backend.service
        ```
    7.  Überprüfen Sie den Status:
        ```bash
        sudo systemctl status daki-backend.service
        ```
    8.  Sehen Sie sich die Logs an:
        ```bash
        journalctl -u daki-backend.service -f
        ```
