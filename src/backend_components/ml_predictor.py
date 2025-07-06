import pandas as pd
import xgboost as xgb # Oder lightgbm
from typing import Dict, Any, List
import logging
import joblib # Für Modell-Speicherung
import os
import datetime

# Annahme: DataPreparation Klasse ist verfügbar
from src.backend_components.data_preparation import DataPreparation

logger = logging.getLogger(__name__)

class MLPredictor:
    """
    Verwaltet das Training, Speichern und die Vorhersage mit Machine Learning Modellen.
    """

    def __init__(self, model_path: str = "data/models/xgboost_model.joblib"):
        self.model = None
        self.model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../', model_path)
        self.data_preparer = DataPreparation() # Instanz der Datenvorbereitung
        self.load_model() # Versuche, das Modell beim Start zu laden

    async def train_model(self, all_historical_data: List[Dict[str, Any]]):
        """
        Trainiert das ML-Modell.
        Args:
            all_historical_data: Alle verfügbaren historischen Daten für das Training.
                                 Dies sollte eine Sammlung von Daten für mehrere Ticker sein.
        """
        logger.info("Starting ML model training...")

        X_train = pd.DataFrame()
        y_train = pd.Series()

        # Hier müsste die Logik zum Aggregieren der Daten für alle Ticker stehen.
        # Für dieses Beispiel nehmen wir an, dass all_historical_data bereits
        # ein DataFrame ist, das alle vorbereiteten Daten enthält.
        # In einer realen Anwendung würden wir hier eine Schleife über Ticker machen
        # und self.data_preparer.prepare_data_for_ml aufrufen.

        # Beispiel: Wenn all_historical_data bereits vorbereitete Daten für alle Ticker enthält
        if not all_historical_data:
            logger.warning("No data available for ML model training.")
            return

        # Annahme: all_historical_data ist eine Liste von Dictionaries, die bereits
        # die notwendigen Features und das Target enthalten, oder wir müssen sie hier vorbereiten.
        # Für die Implementierung nehmen wir an, dass wir einen DataFrame bekommen, der
        # bereits die Features und das Target enthält.
        # Dies ist ein vereinfachter Platzhalter.
        # In der Realität müssten wir hier die Daten für alle Ticker durch die DataPreparation jagen.
        
        # Beispielhaftes DataFrame aus der Liste der Dictionaries erstellen
        temp_df = pd.DataFrame(all_historical_data)
        if 'target' in temp_df.columns:
            X_train = temp_df.drop(columns=['target'])
            y_train = temp_df['target']
        else:
            logger.warning("'target' column not found in training data. Cannot train model.")
            return

        if X_train.empty or y_train.empty:
            logger.warning("No data available for ML model training after preparation.")
            return

        # 2. Modell initialisieren und trainieren
        self.model = xgb.XGBRegressor(
            n_estimators=1000,
            max_depth=6,
            learning_rate=0.01,
            subsample=0.8,
            colsample_bytree=0.8,
            objective='reg:squarederror',
            n_jobs=-1 # Nutze alle verfügbaren Kerne
        )

        self.model.fit(X_train, y_train)
        logger.info("ML model training completed.")

        # 3. Modell speichern
        self._save_model()

    def _save_model(self):
        """Speichert das trainierte Modell auf der Festplatte."""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        if self.model:
            joblib.dump(self.model, self.model_path)
            logger.info(f"ML model saved to {self.model_path}")
        else:
            logger.warning("No model to save. Train the model first.")

    def load_model(self):
        """Lädt ein trainiertes Modell von der Festplatte."""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            logger.info(f"ML model loaded from {self.model_path}")
        else:
            logger.warning(f"No model found at {self.model_path}. Model needs to be trained.")
            self.model = None

    async def predict(self, ticker: str, historical_raw_data: List[Dict[str, Any]]) -> float:
        """
        Macht eine Vorhersage für die 30-Tage Wertsteigerung einer Aktie.
        Args:
            ticker: Das Tickersymbol der Aktie.
            historical_raw_data: Liste von Dictionaries mit historischen Rohdaten, Indikatoren und Scores.
        Returns:
            Die vorhergesagte 30-Tage Wertsteigerung.
        """
        if self.model is None:
            self.load_model() # Versuche, das Modell zu laden, falls noch nicht geschehen
            if self.model is None:
                logger.error("ML model not loaded or trained. Cannot make prediction.")
                return 0.0 # Oder raise Exception

        logger.info(f"Making ML prediction for ticker: {ticker}")

        # 1. Daten für die Vorhersage vorbereiten (nur die neuesten Daten)
        prediction_data_df = await self.data_preparer.prepare_data_for_ml(ticker, historical_raw_data, forecast_period=0) # forecast_period=0, da wir keine zukünftigen Targets haben

        if prediction_data_df.empty:
            logger.warning(f"No sufficient data to make prediction for {ticker}.")
            return 0.0

        # WICHTIG: Nur die Features für die Vorhersage verwenden, nicht das Target
        # Sicherstellen, dass die Spaltenreihenfolge und -namen mit dem Training übereinstimmen
        # Dies ist ein häufiger Fallstrick. Man sollte die Feature-Namen vom Training speichern.
        X_predict = prediction_data_df.drop(columns=['target'], errors='ignore').iloc[-1:].copy()

        prediction = self.model.predict(X_predict)[0]
        logger.info(f"ML prediction for {ticker}: {prediction}")
        return prediction

    async def get_status(self) -> Dict[str, Any]:
        """
        Gibt den aktuellen Status des MLPredictor zurück.
        """
        status = "OK"
        message = "MLPredictor ready"
        details = {"model_loaded": self.model is not None}

        if self.model is None:
            status = "WARNING"
            message = "ML model not loaded."

        return {
            "status": status,
            "message": message,
            "last_checked": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "details": details
        }
