# Entwicklungsanforderungen: Technical Analysis Scoring System

## Projektübersicht

**Ziel:** Entwicklung eines technischen Analyse-Scoring-Systems für 30-Tage Aktienprognosen mit maximaler Wertsteigerung

**Scope:** Scoring-Algorithmus für 7 technische Indikator-Kategorien mit gewichteter Punktevergabe

## Funktionale Anforderungen

### 1. RSI (Relative Strength Index) Scoring
**Gewichtung:** 15% des Gesamtscores

**Anforderungen:**
- Score-Range: -3 bis +3 Punkte
- Überverkauft/Überkauft Erkennung:
  - RSI < 20: +3 Punkte (stark überverkauft)
  - RSI < 30: +2 Punkte (überverkauft)
  - RSI > 80: -3 Punkte (stark überkauft)
  - RSI > 70: -2 Punkte (überkauft)
- Momentum-Wendepunkte:
  - Ausbruch aus RSI < 30: +2 Punkte
  - Durchbruch unter RSI > 70: -2 Punkte
- 50-Linie Kreuzungen:
  - Bullish (von unten): +1 Punkt
  - Bearish (von oben): -1 Punkt
- Trend-Analyse:
  - RSI-Trend vs. 14-Tage-Mittel: ±1 Punkt

### 2. MACD Scoring
**Gewichtung:** 20% des Gesamtscores

**Anforderungen:**
- Score-Range: -3 bis +3 Punkte
- Signal Line Kreuzungen:
  - Bullish unter Nulllinie: +3 Punkte
  - Bullish über Nulllinie: +2 Punkte
  - Bearish über Nulllinie: -3 Punkte
  - Bearish unter Nulllinie: -2 Punkte
- Nulllinie Kreuzungen:
  - MACD über Nulllinie: +2 Punkte
  - MACD unter Nulllinie: -2 Punkte
- Histogram Momentum: ±1 Punkt

### 3. Moving Averages Scoring
**Gewichtung:** 15% des Gesamtscores

**Anforderungen:**
- EMA Perioden: 10, 20, 50 Tage
- Score-Range: -3 bis +3 Punkte
- Preis-Position Bewertung:
  - Preis > EMA10 > EMA20 > EMA50: +3 Punkte
  - Preis < EMA10 < EMA20 < EMA50: -3 Punkte
  - Zwischenstufen: +2/+1 bzw. -2/-1 Punkte
- Golden/Death Cross:
  - EMA10 kreuzt EMA20 von unten: +2 Punkte
  - EMA10 kreuzt EMA20 von oben: -2 Punkte
- EMA-Steigung: ±1 Punkt

### 4. Bollinger Bands Scoring
**Gewichtung:** 10% des Gesamtscores

**Anforderungen:**
- Score-Range: -3 bis +3 Punkte
- Band-Position:
  - Untere 10% des Bands: +2 Punkte
  - Obere 10% des Bands: -2 Punkte
- Band-Durchbrüche:
  - Ausbruch nach oben aus unterem Band: +3 Punkte
  - Rückfall von oberem Band: -3 Punkte
- Mittellinie-Kreuzungen: ±1 Punkt
- Squeeze-Erkennung: ±1 Punkt

### 5. Volume Indikatoren Scoring
**Gewichtung:** 15% des Gesamtscores

**Anforderungen:**
- Score-Range: -3 bis +3 Punkte
- Volume-Bestätigung:
  - Preissteigerung + hohes Volumen: +2 Punkte
  - Preisrückgang + hohes Volumen: -2 Punkte
- OBV (On Balance Volume) Trend: ±2 Punkte
- Volume-Divergenz Erkennung: ±1 Punkt

### 6. Volatilitätsindikatoren Scoring
**Gewichtung:** 10% des Gesamtscores

**Anforderungen:**
- ATR (Average True Range) Analyse
- Bollinger Band Width Analyse
- Score-Range: -3 bis +3 Punkte
- Niedrige Volatilität (Ruhe vor Sturm): +1 Punkt
- Squeeze-Erkennung: +2 Punkte
- Volume Spike bei niedriger Volatilität: +2 Punkte

### 7. Momentum-Indikatoren Scoring
**Gewichtung:** 15% des Gesamtscores

**Anforderungen:**
- Stochastik (%K, %D)
- Rate of Change (5, 10 Tage)
- Score-Range: -3 bis +3 Punkte
- Stochastik Überverkauft/Überkauft: ±2 Punkte
- Stochastik Kreuzungen: ±3 Punkte (kontextabhängig)
- ROC Momentum: ±2 Punkte

### 8. Event-driven Scoring
**Gewichtung:** 10% des Gesamtscores

**Anforderungen:**
- Score-Range: -5 bis +5 Punkte
- Zeitfenster: Nächste 30 Tage
- Kategorien mit spezifischen Multiplikatoren

#### 8.1 Earnings Events (Gewichtung: 3x)
**Zeitrahmen:** 0-7 Tage vor Earnings
```
Earnings Surprise History Analysis:
- Letzte 4 Quartale alle positiv: +3 Punkte
- 3 von 4 Quartalen positiv: +2 Punkte  
- 2 von 4 Quartalen positiv: +1 Punkt
- 1 von 4 Quartalen positiv: 0 Punkte
- 0 von 4 Quartalen positiv: -2 Punkte

Analyst Revision Trend (letzte 30 Tage):
- >50% Upgrades: +2 Punkte
- 25-50% Upgrades: +1 Punkt
- Neutral: 0 Punkte
- 25-50% Downgrades: -1 Punkt
- >50% Downgrades: -2 Punkte

EPS Estimate Dispersion:
- Niedrige Streuung (<5%): +1 Punkt (Konsens)
- Hohe Streuung (>15%): -1 Punkt (Unsicherheit)

Guidance Track Record:
- Management beat eigene Guidance 3/4 Mal: +1 Punkt
- Management missed eigene Guidance 3/4 Mal: -1 Punkt

Vorankündigung/Preannouncement:
- Positive Preannouncement: +2 Punkte
- Negative Preannouncement: -3 Punkte

Maximaler Earnings Score: +5 bis -5 (vor 3x Multiplikator)
```

#### 8.2 FDA/Regulatory Approvals (Gewichtung: 2x)
**Anwendbar:** Biotech, Pharma, Medical Device Unternehmen
```
PDUFA Date Proximity:
- 0-7 Tage vor PDUFA: +3 Punkte
- 8-14 Tage vor PDUFA: +2 Punkte
- 15-30 Tage vor PDUFA: +1 Punkt

Phase Trial Success Probability:
- Phase III Erfolgswahrscheinlichkeit >70%: +2 Punkte
- Phase II/III mit positiven Interimsdaten: +1 Punkt
- Phase I/II erste Daten: +1 Punkt

FDA Breakthrough Designation:
- Breakthrough Therapy Status: +2 Punkte
- Fast Track Status: +1 Punkt
- Orphan Drug Status: +1 Punkt

Regulatory History:
- Unternehmen 3/3 letzte Approvals erfolgreich: +1 Punkt
- Unternehmen 1/3 letzte Approvals erfolgreich: -1 Punkt
- Complete Response Letter (CRL) History: -2 Punkte

Competitive Landscape:
- First-in-Class Drug: +1 Punkt
- Starke Konkurrenz bereits approved: -1 Punkt

Maximaler FDA Score: +5 bis -3 (vor 2x Multiplikator)
```

#### 8.3 Product Launches (Gewichtung: 1.5x)
**Anwendbar:** Tech, Consumer, Auto Sektoren
```
Launch Significance:
- Flagship Product/Major Revenue Driver: +3 Punkte
- Line Extension/Upgrade: +2 Punkte
- Minor Product Update: +1 Punkt

Pre-Launch Indicators:
- Hohe Vorbestellungen/Pre-Orders: +2 Punkte
- Positive Analyst/Media Reviews: +1 Punkt
- Supply Chain Issues/Delays: -2 Punkte

Market Readiness:
- Unumkämpfter Markt: +1 Punkt
- Intensive Konkurrenz: -1 Punkt
- Disruptive Technology: +2 Punkte

Historical Launch Success:
- Letzte 2 Launches erfolgreich (>Erwartungen): +1 Punkt
- Letzte 2 Launches enttäuschend: -1 Punkt

Launch Timing:
- Optimaler Saisonaler Zeitpunkt: +1 Punkt
- Suboptimaler Zeitpunkt: -1 Punkt

Maximaler Product Launch Score: +5 bis -3 (vor 1.5x Multiplikator)
```

#### 8.4 M&A Activity (Gewichtung: 2x)
```
Takeover Rumors/Speculation:
- Seriöse Medienberichte über Interest: +3 Punkte
- Analyst Speculation über Takeover: +2 Punkte
- Unusual Options Activity (hohe Call Volume): +1 Punkt

Activist Investor Involvement:
- Aktivist fordert Verkauf/Spin-off: +2 Punkte
- Aktivist building stake: +1 Punkt

Strategic Rationale:
- Klarer strategischer Fit für Acquirer: +1 Punkt
- Synergien offensichtlich: +1 Punkt
- Anti-Trust Probleme wahrscheinlich: -2 Punkte

Valuation Gap:
- Trading <50% von Sector Peers: +2 Punkte
- Trading <70% von Sector Peers: +1 Punkt
- Premium Valuation: -1 Punkt

Management Resistance:
- Management historically M&A-friendly: +1 Punkt
- Management starke Anti-Takeover Maßnahmen: -1 Punkt

Maximaler M&A Score: +5 bis -2 (vor 2x Multiplikator)
```

#### 8.5 Spin-offs/Divestitures (Gewichtung: 1.5x)
```
Spin-off Announcement:
- Spin-off angekündigt (0-30 Tage): +3 Punkte
- Spin-off erwartet/diskutiert: +1 Punkt

Value Unlock Potential:
- Sum-of-Parts Discount >30%: +2 Punkte
- Sum-of-Parts Discount 15-30%: +1 Punkt

Management Focus:
- Klar definierte Fokussierung nach Spin-off: +1 Punkt
- Portfolio-Simplification: +1 Punkt

Historical Spin-off Performance:
- Sektor historisch positive Spin-off Performance: +1 Punkt

Asset Sale Proceeds:
- Bedeutende Cash-Rückführung geplant: +1 Punkt

Maximaler Spin-off Score: +5 bis 0 (vor 1.5x Multiplikator)
```

#### 8.6 Conference/Presentation Events (Gewichtung: 1x)
```
Conference Significance:
- Major Industry Conference (CES, JPM Healthcare): +2 Punkte
- Investor Day/Capital Markets Day: +2 Punkte
- Sector Conference: +1 Punkt

Presentation Content Expectations:
- New Strategy/Vision erwartet: +1 Punkt
- Technology Demo/Product Preview: +1 Punkt
- Guidance Update erwartet: +1 Punkt

Management Track Record:
- Historisch positive Conference Performance: +1 Punkt
- Historisch enttäuschende Präsentationen: -1 Punkt

Maximaler Conference Score: +3 bis -1 (vor 1x Multiplikator)
```

#### 8.7 Economic/Sector Events (Gewichtung: 1x)
```
Sector-spezifische Events:
- Oil Inventory Reports (Energy): ±2 Punkte
- FOMC Meetings (Financials): ±2 Punkte
- Chip Sales Data (Semiconductors): ±1 Punkt

Regulatory Changes:
- Positive Regulatory Environment: +1 Punkt
- Regulatory Headwinds: -2 Punkte

Seasonal Factors:
- Positive seasonale Trends: +1 Punkt
- Negative seasonale Trends: -1 Punkt

Maximaler Economic Score: +2 bis -2 (vor 1x Multiplikator)
```

#### 8.8 Event Scoring Berechnung
```
def calculate_event_score(events_data):
    base_scores = {
        'earnings': calculate_earnings_score(events_data['earnings']),      # -5 bis +5
        'fda': calculate_fda_score(events_data['fda']),                   # -3 bis +5  
        'product': calculate_product_score(events_data['product']),        # -3 bis +5
        'ma': calculate_ma_score(events_data['ma']),                      # -2 bis +5
        'spinoff': calculate_spinoff_score(events_data['spinoff']),       # 0 bis +5
        'conference': calculate_conference_score(events_data['conf']),     # -1 bis +3
        'economic': calculate_economic_score(events_data['economic'])      # -2 bis +2
    }
    
    multipliers = {
        'earnings': 3.0,
        'fda': 2.0,
        'product': 1.5,
        'ma': 2.0,
        'spinoff': 1.5,
        'conference': 1.0,
        'economic': 1.0
    }
    
    weighted_score = sum(
        base_scores[event] * multipliers[event] 
        for event in base_scores if base_scores[event] != 0
    )
    
    # Normalisierung auf -5 bis +5 mit Min-Max Scaling
    max_possible = 5 * 3.0  # Earnings max weighted score: 15
    min_possible = -5 * 3.0 # Earnings min weighted score: -15
    final_score = normalize_score(weighted_score, min_possible, max_possible, -5, 5)
    
    return {
        'total_event_score': round(final_score, 2),
        'individual_events': base_scores,
        'weighted_events': {k: base_scores[k] * multipliers[k] for k in base_scores},
        'active_events': [k for k, v in base_scores.items() if v != 0]
    }

def normalize_score(value, input_min, input_max, output_min, output_max):
    """
    Min-Max Normalisierung mit Clipping
    
    Args:
        value: Zu normalisierender Wert
        input_min: Minimum der Eingabe-Range
        input_max: Maximum der Eingabe-Range  
        output_min: Minimum der Ausgabe-Range
        output_max: Maximum der Ausgabe-Range
    
    Returns:
        Normalisierter Wert zwischen output_min und output_max
    """
    # Clipping auf Input-Range
    clipped_value = max(input_min, min(input_max, value))
    
    # Vermeide Division durch Null
    if input_max == input_min:
        return (output_min + output_max) / 2
    
    # Min-Max Scaling
    normalized = (clipped_value - input_min) / (input_max - input_min)
    scaled = normalized * (output_max - output_min) + output_min
    
    return scaled

def normalize_total_score(technical_scores, event_score, weights):
    """
    Gesamtscore-Normalisierung für finales Scoring-System
    
    Args:
        technical_scores: Dict der technischen Indikator-Scores (-3 bis +3 jeweils)
        event_score: Event-driven Score (-5 bis +5)
        weights: Gewichtungsschema
    
    Returns:
        Finaler normalisierter Score (-20 bis +20)
    """
    # Berechne gewichteten Score
    weighted_technical = sum(
        technical_scores[indicator] * weights[indicator] 
        for indicator in technical_scores
    )
    weighted_event = event_score * weights['events']
    
    total_weighted = weighted_technical + weighted_event
    
    # Theoretischer Max/Min für Normalisierung
    max_technical = sum(3 * weights[ind] for ind in technical_scores.keys())  # Alle +3
    min_technical = sum(-3 * weights[ind] for ind in technical_scores.keys()) # Alle -3
    max_event = 5 * weights['events']
    min_event = -5 * weights['events']
    
    theoretical_max = max_technical + max_event
    theoretical_min = min_technical + min_event
    
    # Normalisierung auf -20 bis +20
    final_score = normalize_score(
        total_weighted, 
        theoretical_min, 
        theoretical_max, 
        -20, 
        20
    )
    
    return round(final_score, 2)
```

#### 8.9 Datenquellen für Event Detection
```
Earnings Calendar:
- Yahoo Finance Earnings Calendar API
- Alpha Vantage Earnings Calendar
- Quandl Earnings Data

FDA Pipeline:
- ClinicalTrials.gov API
- FDA PDUFA Calendar
- BioPharma Catalyst Databases

M&A Intelligence:
- Thomson Reuters M&A Database
- Bloomberg Terminal
- SEC Filing 13D/13G Monitoring

News/Rumors:
- Financial News APIs (Reuters, Bloomberg)
- Social Media Sentiment (Twitter, Reddit)
- Google Trends für Ticker + Keywords

Conference Calendars:
- Investor Relations Websites
- Industry Association Calendars
- Earnings.com Conference Calendar
```

## Technische Anforderungen

### Eingabedaten
```
Erforderliche Datenfelder pro Indikator:
- RSI: current, previous, 14-day average
- MACD: line, signal, histogram, previous values
- MA: price, EMA10/20/50, previous EMA values
- Bollinger: price, upper/lower/middle bands, previous price
- Volume: current volume, average, OBV current/previous, price current/previous
- Volatility: ATR current/average, BB width current/average, volume spike flag
- Momentum: Stochastic K/D current/previous, ROC 5/10 day
- Events: earnings_data, fda_data, product_data, ma_data, spinoff_data, conference_data, economic_data
```

### Ausgabeformat
```
{
  "total_score": float (-20 bis +20),  # Erweitert um Event-Scoring
  "individual_scores": {
    "rsi": int (-3 bis +3),
    "macd": int (-3 bis +3),
    "ma": int (-3 bis +3),
    "bollinger": int (-3 bis +3),
    "volume": int (-3 bis +3),
    "volatility": int (-3 bis +3),
    "momentum": int (-3 bis +3),
    "events": float (-5 bis +5)
  },
  "event_details": {
    "total_event_score": float (-5 bis +5),
    "individual_events": dict,
    "weighted_events": dict,
    "active_events": list
  },
  "signal_strength": enum ["VERY_STRONG", "STRONG", "MODERATE", "WEAK"],
  "recommendation": enum ["STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"],
  "score_percentage": float (0-100)
}
```

### Gewichtungsschema
```
weights = {
  "rsi": 0.135,          # 15% * 0.9 (um Platz für Events zu schaffen)
  "macd": 0.18,          # 20% * 0.9  
  "ma": 0.135,           # 15% * 0.9
  "bollinger": 0.09,     # 10% * 0.9
  "volume": 0.135,       # 15% * 0.9
  "volatility": 0.09,    # 10% * 0.9
  "momentum": 0.135,     # 15% * 0.9
  "events": 0.10         # 10% für Event-driven Scoring
}
# Summe: 100%
```

### Empfehlungslogik (angepasst für erweiterten Score-Range)
```
Score >= 12: STRONG_BUY    # 60% des Max-Scores (20)
Score >= 6: BUY            # 30% des Max-Scores
Score >= -6: HOLD          # -30% bis +30%
Score >= -12: SELL         # -60% des Min-Scores
Score < -12: STRONG_SELL   # < -60%
```

### Signalstärke-Klassifikation (angepasst)
```
|Score| >= 16: VERY_STRONG  # 80% des Max-Scores
|Score| >= 12: STRONG       # 60% des Max-Scores
|Score| >= 6: MODERATE      # 30% des Max-Scores
|Score| < 6: WEAK           # < 30%
```

## Nicht-funktionale Anforderungen

### Performance
- Berechnung pro Aktie: < 100ms
- Batch-Verarbeitung: 1000 Aktien < 10 Sekunden

### Erweiterbarkeit
- Modulare Implementierung pro Indikator
- Konfigurierbare Gewichtungen
- Einfache Integration neuer Indikatoren

### Validierung
- Input-Validierung für alle Indikatoren
- Score-Range Begrenzung (-3 bis +3 pro Indikator)
- Fehlende Daten-Behandlung

### Logging
- Scoring-Entscheidungen nachvollziehbar
- Indikator-Berechnungen protokollieren
- Performance-Metriken

## Implementierungshinweise

### Architektur
- Klassen-basierte Implementierung
- Separate Methoden pro Indikator
- Factory Pattern für Indikator-Erzeugung

### Fehlerbehandlung
- Graceful Degradation bei fehlenden Indikatoren
- Standardwerte für unvollständige Daten
- Exception Handling für Berechnungsfehler

### Testing
- Unit Tests pro Indikator
- Integration Tests für Gesamtscore
- Edge Cases (extreme Werte, fehlende Daten)

## Akzeptanzkriterien

1. ✅ Alle 7 Indikator-Kategorien implementiert
2. ✅ Scoring-Logik entspricht Spezifikation
3. ✅ Gewichtetes Gesamtscore-System funktional
4. ✅ Performance-Anforderungen erfüllt
5. ✅ Ausgabeformat korrekt
6. ✅ Empfehlungslogik implementiert
7. ✅ Signalstärke-Klassifikation funktional
8. ✅ Input-Validierung vorhanden
9. ✅ Unit Tests mit >90% Coverage
10. ✅ Dokumentation vollständig

## Risiken und Mitigation

**Risiko:** Overfitting auf historische Daten
**Mitigation:** Backtesting mit Out-of-Sample Daten

**Risiko:** Indikator-Korrelation führt zu Bias
**Mitigation:** Korrelationsanalyse und Gewichtungsanpassung

**Risiko:** Performance bei großen Datenmengen
**Mitigation:** Parallelisierung und Caching

## Deliverables

1. **Core Scoring Engine** - Hauptklasse mit allen Indikator-Methoden
2. **Configuration Module** - Gewichtungen und Parameter
3. **Validation Module** - Input/Output Validierung
4. **Test Suite** - Umfassende Tests
5. **Documentation** - API-Dokumentation und Beispiele
6. **Performance Benchmarks** - Laufzeit-Metriken

---

**Status:** In Entwicklung
**Priorität:** Hoch
**Verantwortlich:** Marco Döhler
**Reviewer:** [Reviewername]
