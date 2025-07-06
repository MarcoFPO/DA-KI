import os
import json
import base64
from typing import Any, Dict

class Config:
    _secrets: Dict[str, Any] = {}
    _is_loaded: bool = False

    @classmethod
    def load_secrets(cls):
        if cls._is_loaded:
            return

        env = os.getenv("DAKI_ENV", "development") # Standard ist development

        if env == "development":
            secrets_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../config/dev_secrets.json')
            try:
                with open(secrets_file, 'r') as f:
                    cls._secrets = json.load(f)
                print(f"Secrets loaded from {secrets_file} (Development Mode)")
            except FileNotFoundError:
                print(f"Warning: {secrets_file} not found. Running without dev secrets.")
                cls._secrets = {} # Leeres Dictionary, wenn Datei nicht gefunden
            except json.JSONDecodeError:
                print(f"Error: {secrets_file} is not a valid JSON file.")
                cls._secrets = {}
        elif env == "production":
            print("Loading secrets for Production Mode (via environment variables/DB encryption).")
            prod_secrets = {}
            # Lade den Master-Verschlüsselungsschlüssel
            master_key_b64 = os.getenv("DAKI_MASTER_ENCRYPTION_KEY")
            if master_key_b64:
                try:
                    prod_secrets["system"] = {
                        "master_encryption_key": base64.b64decode(master_key_b64)
                    }
                except Exception as e:
                    print(f"Error decoding DAKI_MASTER_ENCRYPTION_KEY: {e}")
                    # Hier sollte eine kritische Fehlermeldung/Exit erfolgen
            else:
                print("Warning: DAKI_MASTER_ENCRYPTION_KEY not set in production environment.")
                # Hier sollte eine kritische Fehlermeldung/Exit erfolgen

            # Beispiel: Lade andere Umgebungsvariablen, die mit "DAKI_" beginnen
            for key, value in os.environ.items():
                if key.startswith("DAKI_") and key != "DAKI_MASTER_ENCRYPTION_KEY":
                    # Einfache Aufteilung für Top-Level-Keys
                    parts = key[len("DAKI_"):].lower().split('_')
                    current_level = prod_secrets
                    for i, part in enumerate(parts):
                        if i == len(parts) - 1:
                            current_level[part] = value
                        else:
                            current_level = current_level.setdefault(part, {})
            cls._secrets = prod_secrets
        else:
            print(f"Unknown environment: {env}. Loading no secrets.")
            cls._secrets = {}

        cls._is_loaded = True

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Gibt einen Geheimniswert zurück. Für verschachtelte Werte muss der Aufrufer
        die Unter-Keys selbst abrufen.
        Beispiel: Config.get("users")["admin"]["username"]
        """
        if not cls._is_loaded:
            cls.load_secrets() # Lade Geheimnisse, falls noch nicht geschehen
        return cls._secrets.get(key, default)
