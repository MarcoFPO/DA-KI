import abc
from typing import Dict, Any, List, Optional

class DataSourcePlugin(abc.ABC):
    """
    Abstrakte Basisklasse für DA-KI Datenquellen-Plugins.
    Alle Datenquellen-Plugins müssen von dieser Klasse erben und ihre abstrakten Methoden implementieren.
    """

    @abc.abstractmethod
    def get_name(self) -> str:
        """
        Gibt den eindeutigen Namen des Datenquellen-Plugins zurück (z.B. "AlphaVantagePlugin").
        """
        pass

    @abc.abstractmethod
    def get_description(self) -> str:
        """
        Gibt eine kurze Beschreibung des Datenquellen-Plugins zurück.
        """
        pass

    @abc.abstractmethod
    def get_config_schema(self) -> Dict[str, Any]:
        """
        Gibt das Konfigurationsschema für dieses Plugin zurück.
        Dieses Schema wird für die webbasierte Bearbeitung der Plugin-spezifischen Konfigurationen verwendet.
        Beispiel:
        {
            "api_key": {"type": "string", "description": "API Key für den Dienst", "default": ""},
            "max_retries": {"type": "integer", "description": "Maximale Wiederholungsversuche für API-Aufrufe", "default": 3}
        }
        """
        pass

    @abc.abstractmethod
    def initialize(self, config: Dict[str, Any]):
        """
        Initialisiert das Plugin mit seiner spezifischen Konfiguration.
        Diese Methode sollte nach dem Laden des Plugins aufgerufen werden.
        """
        pass

    @abc.abstractmethod
    async def fetch_ohlcv_data(
        self, ticker: str, start_date: str, end_date: str, interval: str
    ) -> List[Dict[str, Any]]:
        """
        Ruft OHLCV (Open, High, Low, Close, Volume) Daten für einen gegebenen Ticker und Datumsbereich ab.
        Args:
            ticker: Aktien-Tickersymbol (z.B. "AAPL").
            start_date: Startdatum im Format YYYY-MM-DD.
            end_date: Enddatum im Format YYYY-MM-DD.
            interval: Datenintervall (z.B. "1d", "1h", "1m").
        Returns:
            Eine Liste von Dictionaries, wobei jedes einen Datenpunkt darstellt.
            Beispiel: [{"date": "YYYY-MM-DD", "open": ..., "high": ..., "low": ..., "close": ..., "volume": ...}]
        """
        pass

    @abc.abstractmethod
    async def fetch_technical_indicators(
        self, ticker: str, indicator_type: str, params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Ruft spezifische technische Indikatordaten für einen gegebenen Ticker ab.
        Args:
            ticker: Aktien-Tickersymbol.
            indicator_type: Typ des Indikators (z.B. "RSI", "MACD", "SMA").
            params: Dictionary von Parametern, die spezifisch für den Indikator sind (z.B. {"time_period": 14}).
        Returns:
            Eine Liste von Dictionaries mit Indikatorwerten.
        """
        pass

    @abc.abstractmethod
    async def fetch_event_data(
        self, ticker: str, event_type: str, start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Ruft ereignisgesteuerte Daten (z.B. Earnings, FDA-Zulassungen) für einen gegebenen Ticker und Datumsbereich ab.
        Args:
            ticker: Aktien-Tickersymbol.
            event_type: Typ des Ereignisses (z.B. "earnings", "fda_approvals", "product_launches").
            start_date: Startdatum im Format YYYY-MM-DD.
            end_date: Enddatum im Format YYYY-MM-DD.
        Returns:
            Eine Liste von Dictionaries mit Ereignisdetails.
        """
        pass

    @abc.abstractmethod
    async def close(self):
        """
        Führt notwendige Bereinigungsarbeiten durch, wenn das Plugin entladen wird oder die Anwendung herunterfährt.
        """
        pass

    @abc.abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Gibt den aktuellen Status des Plugins zurück.
        """
        pass
