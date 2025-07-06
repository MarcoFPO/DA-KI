# Optimale Prognosemethodik für 30-Tage Aktienwertsteigerung

Dieser Abschnitt beschreibt die vorgeschlagene Methodik zur Prognose der 30-Tage-Aktienwertsteigerung im DA-KI-System.

## Architektur der Prognose-Pipeline

Die Prognose erfolgt in einem zweistufigen Prozess, der ein regelbasiertes Scoring-System mit fortschrittlichen Machine-Learning-Modellen kombiniert.

1.  **Stufe 1: Regelbasiertes Scoring (Intelligenz-Komponente)**
    *   Zunächst wird für jede Aktie ein umfassender Score generiert. Dieser Prozess ist detailliert im Dokument `technical_analysis_requirements.md` beschrieben.
    *   Das Scoring-System analysiert technische Indikatoren, Event-Daten und andere Faktoren, um einen normalisierten Score (von -20 bis +20) zu berechnen.
    *   **Zweck:** Dieser Score dient als hoch-kondensiertes, intelligentes "Super-Feature", das eine expertenbasierte Vor-Analyse der Aktie darstellt.

2.  **Stufe 2: Machine Learning Prognose**
    *   Die in diesem Dokument beschriebenen Machine-Learning-Modelle (z.B. XGBoost, LSTM) nutzen diesen Score als eines ihrer wichtigsten Input-Features.
    *   Neben dem Score werden auch die zugrundeliegenden Rohdaten (z.B. Kursdaten, Volumina, Sentiment-Werte) an die Modelle übergeben.
    *   **Ziel:** Die ML-Modelle lernen die komplexen, nicht-linearen Zusammenhänge zwischen dem Score, den Rohdaten und der tatsächlichen zukünftigen Wertentwicklung, um eine präzisere Prognose zu erstellen.

Diese hybride Architektur verbindet die Transparenz und das Expertenwissen des regelbasierten Systems mit der Fähigkeit der Machine-Learning-Modelle, subtile Muster in großen Datenmengen zu erkennen.

## 1. Machine Learning Ensemble Models

### A) Gradient Boosting Frameworks

*   **XGBoost** - Optimiert für tabellarische Daten
    ```python
    XGBRegressor(
        n_estimators=1000,
        max_depth=6,
        learning_rate=0.01,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='reg:squarederror'
    )
    ```

*   **LightGBM** - Schneller, weniger Overfitting
    ```python
    LGBMRegressor(
        num_leaves=31,
        learning_rate=0.05,
        feature_fraction=0.9,
        bagging_fraction=0.8,
        bagging_freq=5
    )
    ```

*   **CatBoost** - Robust gegen Kategoriale Features
    ```python
    CatBoostRegressor(
        iterations=1000,
        depth=6,
        learning_rate=0.03,
        l2_leaf_reg=3
    )
    ```

### B) Random Forest Varianten

*   **Extra Trees** - Reduziert Overfitting
    ```python
    ExtraTreesRegressor(
        n_estimators=500,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2
    )
    ```

## 2. Deep Learning Architekturen

### A) LSTM Networks für Zeitserien

```python
class StockLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, dropout=0.2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size, hidden_size, num_layers,
            batch_first=True, dropout=dropout
        )
        self.attention = nn.MultiheadAttention(hidden_size, 8)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        # Attention Mechanism
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
        return self.fc(attn_out[:, -1, :])
```

### B) Transformer für Sequenzen

*   **Informer** - Optimiert für Zeitserien-Forecasting
    ```python
    class InformerModel:
        def __init__(self, seq_len=60, pred_len=30):
            self.model = Informer(
                enc_in=feature_count,
                dec_in=feature_count,
                c_out=1,
                seq_len=seq_len,
                label_len=15,
                out_len=pred_len,
                factor=3,
                d_model=512,
                n_heads=8,
                e_layers=2,
                d_layers=1
            )
    ```

### C) CNN-LSTM Hybrid

```python
class CNNLSTM(nn.Module):
    def __init__(self):
        super().__init__()
        # 1D CNN für Feature Extraction
        self.conv1 = nn.Conv1d(features, 64, kernel_size=3)
        self.conv2 = nn.Conv1d(64, 128, kernel_size=3)

        # LSTM für Temporal Dependencies
        self.lstm = nn.LSTM(128, 100, 2, batch_first=True)
        self.fc = nn.Linear(100, 1)
```

## 3. Spezialisierte Finanz-Algorithmen

### A) GARCH für Volatilitätsmodellierung

```python
from arch import arch_model

# EGARCH für asymmetrische Volatilität
model = arch_model(
    returns,
    vol='EGARCH',
    p=1, q=1, o=1,
    dist='skewt'  # Skewed Student-t
)
```

### B) Kalman Filter für adaptive Trends

```python
from pykalman import KalmanFilter

# State Space Model für Trend-Following
kf = KalmanFilter(
    transition_matrices=transition_matrix,
    observation_matrices=observation_matrix,
    initial_state_mean=initial_state,
    n_dim_state=2  # Preis + Trend
)
```

### C) Hidden Markov Models für Regime Changes

```python
from hmmlearn import hmm

# Gaussian HMM für Marktregime
model = hmm.GaussianHMM(
    n_components=3,  # Bull/Bear/Sideways
    covariance_type="full"
)
```

## 4. Ensemble & Stacking Strategien

### A) Multi-Level Stacking

```python
# Level 1: Base Models
base_models = [
    ('xgb', XGBRegressor()),
    ('lgb', LGBMRegressor()),
    ('rf', RandomForestRegressor()),
    ('lstm', KerasRegressor(build_fn=create_lstm))
]

# Level 2: Meta-Learner
meta_model = LinearRegression()

stacked_model = StackingRegressor(
    estimators=base_models,
    final_estimator=meta_model,
    cv=TimeSeriesSplit(n_splits=5)
)
```

### B) Weighted Ensemble mit Performance-Tracking

```python
def dynamic_ensemble_weights(models, performance_window=30):
    """Adaptive Gewichtung basierend auf Recent Performance"""
    weights = []
    for model in models:
        recent_performance = calculate_sharpe_ratio(
            model.predictions[-performance_window:]
        )
        weights.append(max(0, recent_performance))

    # Normalisierung
    total_weight = sum(weights)
    return [w/total_weight for w in weights]
```

## 5. Optimierte Feature Engineering Algorithmen

### A) Automated Feature Selection

```python
from sklearn.feature_selection import SelectFromModel
from boruta import BorutaPy

# Boruta für robuste Feature Selection
boruta = BorutaPy(
    RandomForestRegressor(n_estimators=100),
    n_estimators='auto',
    max_iter=100,
    random_state=42
)
```

### B) Technical Indicator Optimization

```python
def optimize_technical_indicators(data, target, lookback_range=(5, 50)):
    """Genetischer Algorithmus für Parameter-Optimierung"""
    best_params = genetic_algorithm(
        objective_function=lambda params: calculate_ic(
            create_indicators(data, params), target
        ),
        param_bounds=lookback_range,
        population_size=100,
        generations=50
    )
    return best_params
```

## 6. Hyperparameter Optimization

### A) Bayesian Optimization

```python
from optuna import create_study

def objective(trial):
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
        'max_depth': trial.suggest_int('max_depth', 3, 10),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3)
    }

    model = XGBRegressor(**params)
    score = cross_val_score(model, X, y, cv=tscv, scoring='neg_mean_squared_error')
    return score.mean()

study = create_study(direction='maximize')
study.optimize(objective, n_trials=100)
```

## 7. Real-time Adaptation Algorithmen

### A) Online Learning mit River

```python
from river import linear_model, preprocessing

# Adaptive Linear Regression
model = (
    preprocessing.StandardScaler() |
    linear_model.LinearRegression(
        optimizer=optim.SGD(lr=0.01),
        l2=0.1
    )
)

# Incremental Updates
for x, y in stream:
    y_pred = model.predict_one(x)
    model.learn_one(x, y)
```

## 8. Empfohlene Model-Pipeline

```python
class OptimalStockPredictor:
    def __init__(self):
        # Ensemble der besten Algorithmen
        self.models = {
            'xgb': XGBRegressor(params_xgb),
            'lgb': LGBMRegressor(params_lgb),
            'lstm': build_lstm_model(),
            'transformer': InformerModel(),
            'garch': GARCHModel()
        }

        self.meta_learner = LinearRegression()
        self.feature_selector = BorutaPy()

    def fit(self, X, y):
        # Feature Selection
        X_selected = self.feature_selector.fit_transform(X, y)

        # Train base models
        predictions = []
        for name, model in self.models.items():
            model.fit(X_selected, y)
            pred = cross_val_predict(model, X_selected, y)
            predictions.append(pred)

        # Train meta-learner
        meta_features = np.column_stack(predictions)
        self.meta_learner.fit(meta_features, y)

    def predict(self, X):
        X_selected = self.feature_selector.transform(X)
        predictions = []
        for model in self.models.values():
            predictions.append(model.predict(X_selected))

        meta_features = np.column_stack(predictions)
        return self.meta_learner.predict(meta_features)
```

## Performance-Benchmarks:

*   XGBoost/LightGBM: 60-70% Accuracy bei Direction Prediction
*   LSTM + Attention: 55-65% mit besserer Risk-Adjusted Returns
*   Ensemble: 65-75% mit reduzierter Volatilität
*   Transformer: 60-70% bei längeren Sequenzen

**Empfehlung:** Starten Sie mit XGBoost/LightGBM Ensemble, erweitern Sie schrittweise um Deep Learning Komponenten.

## Wichtige Limitationen:

**⚠ Risiko-Disclaimer:**
*   Keine Garantie für Profits
*   Hohe Volatilität bei 30-Tage Zeitraum
*   Schwarze Schwäne nicht vorhersagbar
*   Backtesting ≠ Future Performance