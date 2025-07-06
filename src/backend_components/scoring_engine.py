import pandas as pd
from typing import Dict, Any, List, Tuple
import logging
import numpy as np
import datetime

# Annahme: Die Config-Klasse aus dem Geheimnismanagement ist verfügbar
from src.config.config import Config
# Annahme: Datenbank-Zugriffsfunktionen sind verfügbar
# from src.database.data_access import get_historical_data_for_ticker

# Import der technischen Indikatoren Bibliothek
from src.technical_indicators import indicators

logger = logging.getLogger(__name__)

class ScoringEngine:
    """
    Orchestriert die Berechnung des technischen Analyse-Scores für Aktien.
    """

    def __init__(self):
        # Gewichtungen aus der Konfiguration laden
        # Annahme: weights sind in Config unter "scoring_engine.weights" gespeichert
        self.weights = Config.get("scoring_engine", {}).get("weights", {})
        if not self.weights:
            logger.warning("ScoringEngine initialized without weights. Using default weights.")
            # Standardgewichtungen, falls nicht in der Konfig gefunden
            self.weights = {
                "rsi": 0.135,
                "macd": 0.18,
                "ma": 0.135,
                "bollinger": 0.09,
                "volume": 0.135,
                "volatility": 0.09,
                "momentum": 0.135,
                "events": 0.10
            }

    async def calculate_total_score(self, ticker: str, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Berechnet den gesamten technischen Score für einen gegebenen Ticker.

        Args:
            ticker: Das Tickersymbol der Aktie.
            historical_data: Liste von Dictionaries mit historischen Kursdaten.
                             Muss 'date', 'open', 'high', 'low', 'close', 'volume' enthalten.
                             Sollte auch bereits berechnete Indikatoren enthalten, falls verfügbar.

        Returns:
            Ein Dictionary mit dem Gesamtscore, individuellen Scores,
            Signalstärke und Empfehlung.
        """
        logger.info(f"Calculating technical score for ticker: {ticker}")

        if not historical_data:
            logger.warning(f"No historical data provided for {ticker}. Cannot calculate score.")
            return self._create_empty_score_output()

        # Konvertiere Daten in Pandas DataFrame für einfache Berechnung
        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by='date').set_index('date')
        
        # Sicherstellen, dass numerische Spalten korrekt sind
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Individuelle Indikator-Scores berechnen
        individual_scores = {
            "rsi": self._calculate_rsi_score(df),
            "macd": self._calculate_macd_score(df),
            "ma": self._calculate_ma_score(df),
            "bollinger": self._calculate_bollinger_score(df),
            "volume": self._calculate_volume_score(df),
            "volatility": self._calculate_volatility_score(df),
            "momentum": self._calculate_momentum_score(df),
            "events": 0 # Event-Scoring wird in Phase 2, Aufgabe 2 behandelt
        }

        # Gesamtscore normalisieren
        total_score = self._normalize_total_score(individual_scores)

        # Signalstärke und Empfehlung ableiten
        signal_strength = self._derive_signal_strength(total_score)
        recommendation = self._derive_recommendation(total_score)
        score_percentage = self._calculate_score_percentage(total_score)

        output = {
            "total_score": total_score,
            "individual_scores": individual_scores,
            "signal_strength": signal_strength,
            "recommendation": recommendation,
            "score_percentage": score_percentage
        }
        logger.info(f"Finished calculating score for {ticker}: {output['total_score']}")
        return output

    # --- Private Methoden für individuelle Indikator-Scores ---

    def _calculate_rsi_score(self, df: pd.DataFrame) -> int:
        """Berechnet den RSI-Score (-3 bis +3)."""
        if len(df) < 30: # Benötigt ausreichend Daten für RSI und Trend
            logger.warning("Not enough historical data for RSI calculation. Returning neutral score.")
            return 0

        rsi_series = indicators.calculate_rsi(df['close'], period=14)

        if rsi_series.isnull().all() or len(rsi_series) < 2:
            logger.warning("RSI calculation resulted in insufficient valid data. Returning neutral score.")
            return 0

        current_rsi = rsi_series.iloc[-1]
        previous_rsi = rsi_series.iloc[-2]
        rsi_ma14_series = rsi_series.rolling(window=14).mean()
        rsi_ma14 = rsi_ma14_series.iloc[-1]

        score = 0

        # Überverkauft/Überkauft Erkennung
        if current_rsi < 20:
            score += 3
        elif current_rsi < 30:
            score += 2
        elif current_rsi > 80:
            score -= 3
        elif current_rsi > 70:
            score -= 2

        # Momentum-Wendepunkte
        if not pd.isna(previous_rsi):
            if previous_rsi < 30 and current_rsi >= 30:
                score += 2
            if previous_rsi > 70 and current_rsi <= 70:
                score -= 2

        # 50-Linie Kreuzungen
        if not pd.isna(previous_rsi):
            if previous_rsi < 50 and current_rsi >= 50:
                score += 1
            if previous_rsi > 50 and current_rsi <= 50:
                score -= 1

        # Trend-Analyse
        if not pd.isna(rsi_ma14):
            if current_rsi > rsi_ma14:
                score += 1
            elif current_rsi < rsi_ma14:
                score -= 1

        return max(-3, min(3, score))

    def _calculate_macd_score(self, df: pd.DataFrame) -> int:
        """Berechnet den MACD-Score (-3 bis +3)."""
        if len(df) < 30: # Benötigt ausreichend Daten
            logger.warning("Not enough historical data for MACD calculation. Returning neutral score.")
            return 0
        
        macd_df = indicators.calculate_macd(df['close'])
        if macd_df.empty or macd_df['MACD'].isnull().all():
            logger.warning("MACD calculation resulted in insufficient valid data. Returning neutral score.")
            return 0

        current_macd = macd_df['MACD'].iloc[-1]
        current_signal = macd_df['Signal'].iloc[-1]
        current_hist = macd_df['Histogram'].iloc[-1]
        previous_macd = macd_df['MACD'].iloc[-2]
        previous_signal = macd_df['Signal'].iloc[-2]

        score = 0

        # Signal Line Kreuzungen
        if not pd.isna(previous_macd) and not pd.isna(previous_signal):
            if previous_macd < previous_signal and current_macd >= current_signal: # Bullish Cross
                if current_macd < 0: # unter Nulllinie
                    score += 3
                else: # über Nulllinie
                    score += 2
            elif previous_macd > previous_signal and current_macd <= current_signal: # Bearish Cross
                if current_macd > 0: # über Nulllinie
                    score -= 3
                else: # unter Nulllinie
                    score -= 2

        # Nulllinie Kreuzungen
        if not pd.isna(previous_macd):
            if previous_macd < 0 and current_macd >= 0: # MACD über Nulllinie
                score += 2
            elif previous_macd > 0 and current_macd <= 0: # MACD unter Nulllinie
                score -= 2

        # Histogram Momentum
        if not pd.isna(current_hist) and not pd.isna(macd_df['Histogram'].iloc[-2]):
            if current_hist > macd_df['Histogram'].iloc[-2]:
                score += 1
            elif current_hist < macd_df['Histogram'].iloc[-2]:
                score -= 1

        return max(-3, min(3, score))

    def _calculate_ma_score(self, df: pd.DataFrame) -> int:
        """Berechnet den Moving Averages Score (-3 bis +3)."""
        if len(df) < 50: # Benötigt ausreichend Daten für EMA50
            logger.warning("Not enough historical data for Moving Averages calculation. Returning neutral score.")
            return 0

        ema10 = indicators.calculate_ema(df['close'], 10)
        ema20 = indicators.calculate_ema(df['close'], 20)
        ema50 = indicators.calculate_ema(df['close'], 50)

        if ema10.isnull().all() or ema20.isnull().all() or ema50.isnull().all():
            logger.warning("EMA calculation resulted in insufficient valid data. Returning neutral score.")
            return 0

        current_price = df['close'].iloc[-1]
        current_ema10 = ema10.iloc[-1]
        current_ema20 = ema20.iloc[-1]
        current_ema50 = ema50.iloc[-1]

        previous_ema10 = ema10.iloc[-2]
        previous_ema20 = ema20.iloc[-2]

        score = 0

        # Preis-Position Bewertung
        if current_price > current_ema10 and current_ema10 > current_ema20 and current_ema20 > current_ema50:
            score += 3
        elif current_price < current_ema10 and current_ema10 < current_ema20 and current_ema20 < current_ema50:
            score -= 3
        elif current_price > current_ema10 and current_ema10 > current_ema20:
            score += 2
        elif current_price < current_ema10 and current_ema10 < current_ema20:
            score -= 2
        elif current_price > current_ema10:
            score += 1
        elif current_price < current_ema10:
            score -= 1

        # Golden/Death Cross
        if not pd.isna(previous_ema10) and not pd.isna(previous_ema20):
            if previous_ema10 < previous_ema20 and current_ema10 >= current_ema20: # Golden Cross
                score += 2
            elif previous_ema10 > previous_ema20 and current_ema10 <= current_ema20: # Death Cross
                score -= 2

        # EMA-Steigung (vereinfacht: Vergleich mit vorherigem Wert)
        if not pd.isna(previous_ema10) and current_ema10 > previous_ema10:
            score += 1
        elif not pd.isna(previous_ema10) and current_ema10 < previous_ema10:
            score -= 1

        return max(-3, min(3, score))

    def _calculate_bollinger_score(self, df: pd.DataFrame) -> int:
        """Berechnet den Bollinger Bands Score (-3 bis +3)."""
        if len(df) < 20: # Benötigt ausreichend Daten
            logger.warning("Not enough historical data for Bollinger Bands calculation. Returning neutral score.")
            return 0

        bb_df = indicators.calculate_bollinger_bands(df['close'])
        if bb_df.empty or bb_df['Middle'].isnull().all():
            logger.warning("Bollinger Bands calculation resulted in insufficient valid data. Returning neutral score.")
            return 0

        current_price = df['close'].iloc[-1]
        current_upper = bb_df['Upper'].iloc[-1]
        current_middle = bb_df['Middle'].iloc[-1]
        current_lower = bb_df['Lower'].iloc[-1]

        score = 0

        # Band-Position
        if not pd.isna(current_lower) and not pd.isna(current_upper):
            band_range = current_upper - current_lower
            if band_range > 0: # Vermeide Division durch Null
                lower_10_percent = current_lower + (band_range * 0.1)
                upper_10_percent = current_upper - (band_range * 0.1)

                if current_price < lower_10_percent:
                    score += 2
                elif current_price > upper_10_percent:
                    score -= 2

        # Band-Durchbrüche (vereinfacht: nur aktueller Durchbruch)
        if not pd.isna(current_lower) and current_price < current_lower: # Ausbruch nach unten
            score -= 3
        elif not pd.isna(current_upper) and current_price > current_upper: # Ausbruch nach oben
            score += 3

        # Mittellinie-Kreuzungen
        if not pd.isna(current_middle) and not pd.isna(df['close'].iloc[-2]):
            previous_price = df['close'].iloc[-2]
            if previous_price < current_middle and current_price >= current_middle: # Bullish Cross
                score += 1
            elif previous_price > current_middle and current_price <= current_middle: # Bearish Cross
                score -= 1

        # Squeeze-Erkennung (vereinfacht: Bandbreite im Vergleich zu historischem Durchschnitt)
        # Dies erfordert eine komplexere Logik, hier nur ein Platzhalter
        # if (current_upper - current_lower) < (bb_df['Upper'] - bb_df['Lower']).mean() * 0.8:
        #     score += 1

        return max(-3, min(3, score))

    def _calculate_volume_score(self, df: pd.DataFrame) -> int:
        """Berechnet den Volume Indikatoren Score (-3 bis +3)."""
        if len(df) < 2: # Benötigt mindestens 2 Datenpunkte
            logger.warning("Not enough historical data for Volume Indicators calculation. Returning neutral score.")
            return 0

        current_volume = df['volume'].iloc[-1]
        previous_volume = df['volume'].iloc[-2]
        current_price = df['close'].iloc[-1]
        previous_price = df['close'].iloc[-2]

        score = 0

        # Volume-Bestätigung
        if not pd.isna(current_volume) and not pd.isna(previous_volume) and not pd.isna(current_price) and not pd.isna(previous_price):
            if current_price > previous_price and current_volume > previous_volume * 1.5: # Preissteigerung + hohes Volumen
                score += 2
            elif current_price < previous_price and current_volume > previous_volume * 1.5: # Preisrückgang + hohes Volumen
                score -= 2

        # OBV (On Balance Volume) Trend (vereinfacht)
        # OBV müsste hier berechnet werden. Für die Planung nehmen wir an, dass es verfügbar ist.
        # if df['obv'].iloc[-1] > df['obv'].iloc[-2]:
        #     score += 2
        # elif df['obv'].iloc[-1] < df['obv'].iloc[-2]:
        #     score -= 2

        # Volume-Divergenz Erkennung (sehr komplex, hier nur Platzhalter)
        # if price_trend_up and volume_trend_down:
        #     score -= 1
        # elif price_trend_down and volume_trend_up:
        #     score += 1

        return max(-3, min(3, score))

    def _calculate_volatility_score(self, df: pd.DataFrame) -> int:
        """Berechnet den Volatilitätsindikatoren Score (-3 bis +3)."""
        if len(df) < 14: # Benötigt ausreichend Daten für ATR
            logger.warning("Not enough historical data for Volatility Indicators calculation. Returning neutral score.")
            return 0

        atr_series = indicators.calculate_atr(df['high'], df['low'], df['close'])
        bb_df = indicators.calculate_bollinger_bands(df['close'])

        if atr_series.isnull().all() or bb_df.empty or bb_df['Upper'].isnull().all():
            logger.warning("Volatility calculation resulted in insufficient valid data. Returning neutral score.")
            return 0

        current_atr = atr_series.iloc[-1]
        current_bb_width = bb_df['Upper'].iloc[-1] - bb_df['Lower'].iloc[-1]

        score = 0

        # Niedrige Volatilität (Ruhe vor Sturm) - Vergleich mit historischem Durchschnitt
        if not pd.isna(current_atr) and not pd.isna(atr_series.mean()):
            if current_atr < atr_series.mean() * 0.7: # ATR ist deutlich unter dem Durchschnitt
                score += 1
        
        if not pd.isna(current_bb_width) and not pd.isna((bb_df['Upper'] - bb_df['Lower']).mean()):
            if current_bb_width < (bb_df['Upper'] - bb_df['Lower']).mean() * 0.7: # BB-Breite ist deutlich unter dem Durchschnitt
                score += 1

        # Squeeze-Erkennung (stärker als nur niedrige Volatilität)
        # Dies erfordert eine komplexere Logik, z.B. Bollinger Band Squeeze Indikator
        # if is_bollinger_squeeze(df): # Annahme: Funktion existiert
        #     score += 2

        # Volume Spike bei niedriger Volatilität (sehr komplex, hier nur Platzhalter)
        # if current_volume > df['volume'].mean() * 2 and current_atr < atr_series.mean() * 0.5:
        #     score += 2

        return max(-3, min(3, score))

    def _calculate_momentum_score(self, df: pd.DataFrame) -> int:
        """Berechnet den Momentum-Indikatoren Score (-3 bis +3)."""
        if len(df) < 14: # Benötigt ausreichend Daten für Stochastik
            logger.warning("Not enough historical data for Momentum Indicators calculation. Returning neutral score.")
            return 0

        stoch_df = indicators.calculate_stochastic_oscillator(df['high'], df['low'], df['close'])
        roc5 = indicators.calculate_roc(df['close'], 5)
        roc10 = indicators.calculate_roc(df['close'], 10)

        if stoch_df.empty or stoch_df['K'].isnull().all() or roc5.isnull().all() or roc10.isnull().all():
            logger.warning("Momentum calculation resulted in insufficient valid data. Returning neutral score.")
            return 0

        current_stoch_k = stoch_df['K'].iloc[-1]
        current_stoch_d = stoch_df['D'].iloc[-1]
        previous_stoch_k = stoch_df['K'].iloc[-2]
        previous_stoch_d = stoch_df['D'].iloc[-2]
        current_roc5 = roc5.iloc[-1]
        current_roc10 = roc10.iloc[-1]

        score = 0

        # Stochastik Überverkauft/Überkauft
        if current_stoch_k < 20 and current_stoch_d < 20:
            score += 2
        elif current_stoch_k > 80 and current_stoch_d > 80:
            score -= 2

        # Stochastik Kreuzungen (%K kreuzt %D)
        if not pd.isna(previous_stoch_k) and not pd.isna(previous_stoch_d):
            if previous_stoch_k < previous_stoch_d and current_stoch_k >= current_stoch_d: # Bullish Cross
                score += 3
            elif previous_stoch_k > previous_stoch_d and current_stoch_k <= current_stoch_d: # Bearish Cross
                score -= 3

        # ROC Momentum
        if not pd.isna(current_roc5) and not pd.isna(current_roc10):
            if current_roc5 > 0 and current_roc10 > 0:
                score += 2
            elif current_roc5 < 0 and current_roc10 < 0:
                score -= 2

        return max(-3, min(3, score))

    # --- Private Hilfsmethoden für Gesamtscore-Berechnung und Empfehlungen ---

    def _normalize_total_score(self, individual_scores: Dict[str, int]) -> float:
        """
        Normalisiert den Gesamtscore basierend auf den individuellen Scores und Gewichtungen.
        Verwendet die Logik aus technical_analysis_requirements.md (Abschnitt 8.8).
        """
        weighted_technical = sum(
            individual_scores[indicator] * self.weights.get(indicator, 0)
            for indicator in individual_scores if indicator != "events"
        )
        weighted_event = individual_scores.get("events", 0) * self.weights.get("events", 0)

        total_weighted = weighted_technical + weighted_event

        # Theoretischer Max/Min für Normalisierung (aus technical_analysis_requirements.md)
        # Diese Werte müssen aus den Spezifikationen der einzelnen Indikatoren abgeleitet werden.
        # Für die Planung verwenden wir die Werte aus technical_analysis_requirements.md
        # Max/Min für technische Indikatoren ist -3 bis +3
        # Max/Min für Events ist -5 bis +5

        max_technical_score_per_indicator = 3
        min_technical_score_per_indicator = -3
        max_event_score = 5
        min_event_score = -5

        max_technical_weighted = sum(max_technical_score_per_indicator * self.weights.get(ind, 0)
                                     for ind in ["rsi", "macd", "ma", "bollinger", "volume", "volatility", "momentum"])
        min_technical_weighted = sum(min_technical_score_per_indicator * self.weights.get(ind, 0)
                                     for ind in ["rsi", "macd", "ma", "bollinger", "volume", "volatility", "momentum"])

        max_event_weighted = max_event_score * self.weights.get("events", 0)
        min_event_weighted = min_event_score * self.weights.get("events", 0)

        theoretical_max = max_technical_weighted + max_event_weighted
        theoretical_min = min_technical_weighted + min_event_weighted

        # Sicherstellen, dass keine Division durch Null erfolgt
        if theoretical_max == theoretical_min:
            return 0.0 # Oder einen anderen sinnvollen Standardwert

        # Min-Max Normalisierung auf -20 bis +20
        normalized = (total_weighted - theoretical_min) / (theoretical_max - theoretical_min)
        final_score = normalized * (20 - (-20)) + (-20)

        return round(final_score, 2)

    def _derive_signal_strength(self, total_score: float) -> str:
        """Leitet die Signalstärke aus dem Gesamtscore ab."""
        abs_score = abs(total_score)
        if abs_score >= 16:
            return "VERY_STRONG"
        elif abs_score >= 12:
            return "STRONG"
        elif abs_score >= 6:
            return "MODERATE"
        else:
            return "WEAK"

    def _derive_recommendation(self, total_score: float) -> str:
        """Leitet die Empfehlung aus dem Gesamtscore ab."""
        if total_score >= 12:
            return "STRONG_BUY"
        elif total_score >= 6:
            return "BUY"
        elif total_score >= -6:
            return "HOLD"
        elif total_score >= -12:
            return "SELL"
        else:
            return "STRONG_SELL"

    def _calculate_score_percentage(self, total_score: float) -> float:
        """Berechnet den Score als Prozentwert (0-100)."""
        # Normalisierung von -20 bis +20 auf 0 bis 100
        return round(((total_score + 20) / 40) * 100, 2)

    def _create_empty_score_output(self) -> Dict[str, Any]:
        """Erstellt eine leere Score-Ausgabe bei fehlenden Daten."""
        return {
            "total_score": 0.0,
            "individual_scores": {},
            "signal_strength": "WEAK",
            "recommendation": "HOLD",
            "score_percentage": 50.0
        }

    async def get_status(self) -> Dict[str, Any]:
        """
        Gibt den aktuellen Status der ScoringEngine zurück.
        """
        # Hier könnte komplexere Logik stehen, z.B. ob alle Indikatoren geladen sind,
        # ob es Fehler bei Berechnungen gab etc.
        return {
            "status": "OK",
            "message": "ScoringEngine ready",
            "last_checked": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "details": {
                "weights_loaded": bool(self.weights)
            }
        }
