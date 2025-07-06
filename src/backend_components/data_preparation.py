import pandas as pd
from typing import Dict, Any, List
import logging
import datetime

logger = logging.getLogger(__name__)

class DataPreparation:
    """
    Bereitet Daten für Machine Learning Modelle vor, inklusive Feature Engineering.
    """

    def __init__(self):
        pass

    async def prepare_data_for_ml(self, ticker: str, historical_raw_data: List[Dict[str, Any]], lookback_period: int = 90, forecast_period: int = 30) -> pd.DataFrame:
        """
        Ruft historische Daten ab, führt Feature Engineering durch und berechnet die Zielvariable.

        Args:
            ticker: Das Tickersymbol der Aktie.
            historical_raw_data: Liste von Dictionaries mit historischen Rohdaten, Indikatoren und Scores.
            lookback_period: Anzahl der Tage, die für die Feature-Berechnung zurückgeschaut werden sollen.
            forecast_period: Anzahl der Tage, für die die Wertsteigerung vorhergesagt werden soll.

        Returns:
            Ein Pandas DataFrame mit Features und der Zielvariable.
        """
        logger.info(f"Preparing ML data for ticker: {ticker}")

        if not historical_raw_data:
            logger.warning(f"No sufficient historical data found for {ticker} for ML preparation.")
            return pd.DataFrame()

        df = pd.DataFrame(historical_raw_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by='date').set_index('date')

        # 2. Feature Engineering
        features_df = df.copy()

        # Beispiel: Lagged Features für Schlusskurse und RSI
        features_df['close_lag1'] = features_df['close'].shift(1)
        features_df['rsi_lag1'] = features_df['rsi'].shift(1)

        # Beispiel: Rolling Mean für Schlusskurse
        features_df['close_rolling_mean5'] = features_df['close'].rolling(window=5).mean()

        # Integration der Scores (angenommen, sie sind bereits in historical_raw_data enthalten)
        # features_df['technical_score'] = features_df['total_technical_score']
        # features_df['event_score'] = features_df['total_event_score']

        # 3. Zielvariable berechnen (30-Tage Wertsteigerung)
        # Die Zielvariable ist die prozentuale Änderung des Schlusskurses in den nächsten 'forecast_period' Tagen
        features_df['target'] = (features_df['close'].shift(-forecast_period) / features_df['close']) - 1

        # Entferne Zeilen mit NaN-Werten, die durch Shift-Operationen entstehen
        features_df = features_df.dropna()

        logger.info(f"ML data prepared for {ticker}. Shape: {features_df.shape}")
        return features_df

    async def get_status(self) -> Dict[str, Any]:
        """
        Gibt den aktuellen Status der DataPreparation Komponente zurück.
        """
        return {
            "status": "OK",
            "message": "DataPreparation ready",
            "last_checked": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "details": {}
        }
