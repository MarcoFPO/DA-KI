import pandas as pd
import numpy as np

def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    Berechnet den Relative Strength Index (RSI).
    Args:
        prices: Eine Pandas Series von Schlusskursen.
        period: Die Periode für die RSI-Berechnung (Standard: 14).
    Returns:
        Eine Pandas Series mit den berechneten RSI-Werten.
    """
    # Berechnung der Preisänderungen
    deltas = prices.diff()

    # Gewinne (positive Änderungen) und Verluste (negative Änderungen)
    gains = deltas.where(deltas > 0, 0)
    losses = -deltas.where(deltas < 0, 0)

    # Durchschnittliche Gewinne und Verluste über die Periode
    # Verwendung von ewm (Exponentially Weighted Moving Average) für RSI-Berechnung
    avg_gain = gains.ewm(span=period, adjust=False).mean()
    avg_loss = losses.ewm(span=period, adjust=False).mean()

    # Relative Stärke (RS)
    rs = avg_gain / avg_loss
    rs = rs.replace([np.inf, -np.inf], np.nan) # Unendlich durch NaN ersetzen

    # RSI-Berechnung
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(prices: pd.Series, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> pd.DataFrame:
    """
    Berechnet MACD (Moving Average Convergence Divergence), Signal Line und Histogram.
    Args:
        prices: Eine Pandas Series von Schlusskursen.
        fast_period: Periode für den schnellen EMA.
        slow_period: Periode für den langsamen EMA.
        signal_period: Periode für den Signal-EMA des MACD.
    Returns:
        Ein Pandas DataFrame mit 'MACD', 'Signal' und 'Histogram'.
    """
    ema_fast = prices.ewm(span=fast_period, adjust=False).mean()
    ema_slow = prices.ewm(span=slow_period, adjust=False).mean()

    macd = ema_fast - ema_slow
    signal = macd.ewm(span=signal_period, adjust=False).mean()
    histogram = macd - signal

    return pd.DataFrame({'MACD': macd, 'Signal': signal, 'Histogram': histogram})


def calculate_ema(prices: pd.Series, period: int) -> pd.Series:
    """
    Berechnet den Exponential Moving Average (EMA).
    Args:
        prices: Eine Pandas Series von Schlusskursen.
        period: Die Periode für die EMA-Berechnung.
    Returns:
        Eine Pandas Series mit den berechneten EMA-Werten.
    """
    return prices.ewm(span=period, adjust=False).mean()


def calculate_bollinger_bands(prices: pd.Series, window: int = 20, num_std_dev: int = 2) -> pd.DataFrame:
    """
    Berechnet die Bollinger Bänder (Middle, Upper, Lower).
    Args:
        prices: Eine Pandas Series von Schlusskursen.
        window: Die Periode für den gleitenden Durchschnitt.
        num_std_dev: Anzahl der Standardabweichungen für die Bänder.
    Returns:
        Ein Pandas DataFrame mit 'Middle', 'Upper' und 'Lower' Bändern.
    """
    middle_band = prices.rolling(window=window).mean()
    std_dev = prices.rolling(window=window).std()
    upper_band = middle_band + (std_dev * num_std_dev)
    lower_band = middle_band - (std_dev * num_std_dev)

    return pd.DataFrame({'Middle': middle_band, 'Upper': upper_band, 'Lower': lower_band})


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    Berechnet den Average True Range (ATR).
    Args:
        high: Eine Pandas Series der Hochkurse.
        low: Eine Pandas Series der Tiefkurse.
        close: Eine Pandas Series der Schlusskurse.
        period: Die Periode für die ATR-Berechnung.
    Returns:
        Eine Pandas Series mit den berechneten ATR-Werten.
    """
    tr1 = high - low
    tr2 = np.abs(high - close.shift(1))
    tr3 = np.abs(low - close.shift(1))
    true_range = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
    atr = true_range.ewm(span=period, adjust=False).mean()
    return atr


def calculate_stochastic_oscillator(high: pd.Series, low: pd.Series, close: pd.Series, k_period: int = 14, d_period: int = 3) -> pd.DataFrame:
    """
    Berechnet den Stochastischen Oszillator (%K und %D).
    Args:
        high: Eine Pandas Series der Hochkurse.
        low: Eine Pandas Series der Tiefkurse.
        close: Eine Pandas Series der Schlusskurse.
        k_period: Die Periode für %K.
        d_period: Die Periode für %D (gleitender Durchschnitt von %K).
    Returns:
        Ein Pandas DataFrame mit '%K' und '%D'.
    """
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()

    percent_k = ((close - lowest_low) / (highest_high - lowest_low)) * 100
    percent_d = percent_k.rolling(window=d_period).mean()

    return pd.DataFrame({'K': percent_k, 'D': percent_d})


def calculate_roc(prices: pd.Series, period: int) -> pd.Series:
    """
    Berechnet die Rate of Change (ROC).
    Args:
        prices: Eine Pandas Series von Schlusskursen.
        period: Die Periode für die ROC-Berechnung.
    Returns:
        Eine Pandas Series mit den berechneten ROC-Werten.
    """
    return (prices / prices.shift(period) - 1) * 100

# Hier werden später weitere Funktionen für EMA, Bollinger Bands etc. folgen






