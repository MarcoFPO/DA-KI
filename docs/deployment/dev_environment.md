# Entwicklungsumgebung im LXC-Container

Der LXC-Container dient auch als komfortable Entwicklungsumgebung.

## 1. Tools
Folgende Entwicklungstools werden installiert:
*   **Texteditoren:** `vim`, `nano`, `mc` (enthält `mcedit`)
*   **Systemüberwachung:** `htop`
*   **Terminal-Multiplexer:** `tmux`, `screen`
*   **Debugging-Tools:** Python (`pdb`, `ipdb`), Node.js-Debugger
*   **Weitere nützliche Tools:** `jq`, `tree`

## 2. Zugriff
SSH-Zugriff auf den Container ist für die Entwicklung konfiguriert (z.B. Key-basierte Authentifizierung für den Benutzer `mdoehler`).

## 3. Port-Mapping
Port-Weiterleitungen vom Proxmox Host zum LXC-Container werden für Entwicklungszwecke konfiguriert (z.B. für den Web-GUI-Entwicklungsserver auf Port 3000 und den Backend-Entwicklungsserver auf Port 8000).
