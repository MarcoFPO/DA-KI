# Backend-Kernkomponenten

Dieses Dokument beschreibt die zentralen Komponenten des DA-KI-Backends.

## 1. Technische Indikatoren Bibliothek
Eine interne Python-Bibliothek (`src/technical_indicators/`) wird entwickelt, um die Rohwerte von technischen Indikatoren (z.B. RSI, MACD, EMA, Bollinger Bands) zu berechnen. Diese Funktionen nehmen Rohdaten (z.B. Pandas Series von Schlusskursen) entgegen und geben die berechneten Indikatorwerte zurück.

## 2. ScoringEngine
Die `ScoringEngine` ist eine zentrale Python-Klasse, die den gesamten technischen Scoring-Prozess orchestriert. Sie:
*   Berechnet den Gesamtscore für eine Aktie.
*   Ruft individuelle Indikator-Scoring-Funktionen auf (die die interne technische Indikatoren-Bibliothek nutzen).
*   Sammelt die Ergebnisse und berechnet den gewichteten Gesamtscore.
*   Normalisiert den Gesamtscore und leitet Empfehlung und Signalstärke ab.
*   Ist modular aufgebaut, mit separaten Methoden für jede Indikator-Kategorie.

## 3. EventScoringEngine
Die `EventScoringEngine` ist eine zentrale Python-Klasse, die den Event-driven Score für Aktien berechnet. Sie:
*   Nimmt Event-Daten von Datenquellen-Plugins entgegen.
*   Berechnet individuelle Scores für jede Event-Kategorie (z.B. Earnings, FDA, Product Launches) basierend auf detaillierten Regeln.
*   Wendete Multiplikatoren auf die individuellen Event-Scores an.
*   Normalisiert den gewichteten Event-Score auf einen Bereich von -5 bis +5.

## 4. ML Data Preparation
Eine dedizierte Komponente (`DataPreparation` Klasse) ist für die Vorbereitung der Daten für Machine Learning Modelle zuständig. Dies beinhaltet:
*   **Datenabruf und Aggregation:** Abrufen von historischen OHLCV-Daten, technischen Indikatoren und Event-Scores aus der SQLite-Datenbank.
*   **Feature Engineering:** Erstellung von Features aus Rohdaten und Scores (z.B. Lagged Features, Rolling Statistics, Verhältnisse, Integration von Technical- und Event-Scores).
*   **Zielvariable:** Berechnung der Zielvariable (z.B. 30-Tage Aktienwertsteigerung) aus den historischen Daten.
*   **Datenformat:** Bereitstellung der Daten im Pandas DataFrame-Format für ML-Modelle.

## 5. ML Predictor
Die `MLPredictor` ist eine zentrale Python-Klasse, die für das Training, die Speicherung und die Durchführung von Vorhersagen mit Machine Learning Modellen zuständig ist. Sie:
*   Nutzt die `DataPreparation` Klasse, um Features und Zielvariable zu erhalten.
*   Trainiert ML-Modelle (initial XGBoost/LightGBM) unter Verwendung von Kreuzvalidierung.
*   **Unterstützt Online Learning:** Kann Modelle inkrementell mit neuen, online verfügbaren Daten anpassen, um eine kontinuierliche Anpassung an aktuelle Marktbedingungen zu ermöglichen (z.B. unter Verwendung von Bibliotheken wie `River`).
*   Speichert und lädt trainierte Modelle (z.B. mit `joblib`).
*   Führt Vorhersagen für neue Daten durch.
