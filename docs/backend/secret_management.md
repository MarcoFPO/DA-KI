# Geheimnismanagement

Das Projekt implementiert eine differenzierte Strategie für das Management von Geheimnissen (API-Schlüssel, Passwörter) basierend auf der Umgebung (Entwicklung vs. Produktion).

## 1. `dev_secrets.json` (Entwicklungsumgebung)
*   **Struktur:** Eine lokale, von Git ignorierte JSON-Datei (`dev_secrets.json`) speichert Geheimnisse im Klartext in einer hierarchischen Struktur (z.B. `database.url`, `api_keys.yahoo_finance`, `users.admin.username`).
    ```json
    {
        "database": {
            "url": "sqlite:///./data/daki.db"
        },
        "api_keys": {
            "yahoo_finance": "your_yahoo_finance_dev_api_key",
            "alpha_vantage": "your_alpha_vantage_dev_api_key",
            "broker": {
                "key": "your_broker_dev_api_key",
                "secret": "your_broker_dev_api_secret"
            }
        },
        "users": {
            "admin": {
                "username": "dev_admin",
                "password": "dev_password_in_plaintext"
            }
        },
        "system": {
            "master_encryption_key": "your_dev_master_key_for_encryption" # Für Entwicklung
        }
    }
    ```
*   **Zugriff:** Eine zentrale `Config`-Klasse liest diese Datei, wenn die Anwendung im Entwicklungsmodus (`DAKI_ENV=development`) läuft. Der Zugriff auf verschachtelte Werte erfolgt durch explizites Abrufen der Unter-Keys (z.B. `Config.get("users")["admin"]["username"]`).

## 2. Passwort-Hashing (Produktionsumgebung)
*   **Algorithmus:** Argon2 oder bcrypt (empfohlen: Argon2) unter Verwendung der Python-Bibliothek `passlib`.
*   **Implementierung:** Passwörter werden beim Speichern oder Aktualisieren gehasht. Die Verifikation erfolgt durch Vergleich des eingegebenen Passworts mit dem gespeicherten Hash.

## 3. API-Schlüssel-Verschlüsselung (Produktionsumgebung)
*   **Algorithmus:** AES-256-GCM unter Verwendung der Python-Bibliothek `cryptography`.
*   **Implementierung:** Broker-API-Schlüssel werden vor der Speicherung in der Datenbank verschlüsselt. Der Verschlüsselungsprozess verwendet einen `master key`, einen zufälligen Nonce (IV) und einen Authentifizierungs-Tag. Das Ergebnis (Chiffretext, IV, Tag) wird in der Datenbank gespeichert.

## 4. Master Key Bereitstellung (Produktionsumgebung)
*   **Methode:** Der `master key` (32 Bytes, 256 Bit, kryptografisch sicher, Base64-kodiert) wird als Umgebungsvariable (`DAKI_MASTER_ENCRYPTION_KEY`) auf dem LXC-Container gesetzt, bevor die Anwendung gestartet wird (z.B. in der `systemd` Service-Datei).
*   **Zugriff:** Die `Config`-Klasse liest diesen Schlüssel im Produktionsmodus aus der Umgebungsvariable.
