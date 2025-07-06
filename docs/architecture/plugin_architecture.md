# Plugin-Architektur

Das System ist auf einem dynamischen Plugin-Konzept aufgebaut, um maximale Modularität und Erweiterbarkeit zu gewährleisten.

## 1. Plugin-Verzeichnisstruktur
Plugins werden in dedizierten Unterverzeichnissen innerhalb von `src/plugins/` organisiert. Jedes Plugin sollte in einem eigenen Python-Paket (Unterverzeichnis mit `__init__.py`) liegen.

Beispiel:
```
src/
└── plugins/
    └── data_sources/
        ├── __init__.py
        ├── alpha_vantage_plugin/
        │   ├── __init__.py
        │   └── alpha_vantage.py
        └── yahoo_finance_plugin/
            ├── __init__.py
            └── yahoo_finance.py
```

## 2. Interface-Definition (Python)
Plugins müssen eine spezifische abstrakte Basisklasse implementieren, um eine einheitliche Schnittstelle zum Hauptsystem zu gewährleisten.

Für Datenquellen-Plugins wird die abstrakte Basisklasse `DataSourcePlugin` verwendet. Diese definiert Methoden wie `get_name()`, `get_description()`, `get_config_schema()`, `initialize()`, `fetch_ohlcv_data()`, `fetch_technical_indicators()`, `fetch_event_data()` und `close()`. Alle `fetch_...` Methoden sind asynchron (`async def`).

## 3. Dynamisches Laden
Das Hauptsystem nutzt `importlib.import_module()` und `inspect` um Plugins zur Laufzeit zu erkennen, zu importieren und zu instantiieren. Fehler beim Laden werden robust behandelt.

## 4. Plugin-Registrierung
Geladene Plugin-Instanzen werden im Hauptsystem registriert und können über ihre eindeutigen Namen angesprochen werden.

## 5. Plugin-Management (PluginManager)
Ein zentraler `PluginManager` ist für das Laden, Verwalten und Bereitstellen der Plugin-Instanzen zuständig. Seine Aufgaben umfassen:
*   **Scan:** Scannt das Plugin-Verzeichnis beim Anwendungsstart.
*   **Laden:** Nutzt den dynamischen Import-Mechanismus zum Laden der Plugin-Module.
*   **Validierung:** Überprüft die Gültigkeit der geladenen Plugin-Klassen (Erben von `DataSourcePlugin`).
*   **Instanziierung:** Erstellt Instanzen der validen Plugin-Klassen.
*   **Registrierung:** Speichert die instanziierten Plugins in einem zugänglichen Format (z.B. Dictionary).
*   **Bereitstellung:** Bietet Methoden zum Zugriff auf die geladenen Plugin-Instanzen.
*   **Initialisierung:** Ruft die `initialize()`-Methode der Plugins nach dem Laden und Konfigurieren auf.
*   **Herunterfahren:** Ruft die `close()`-Methode der Plugins beim Herunterfahren der Anwendung auf.
