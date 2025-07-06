# Audit-Trail & Nachvollziehbarkeit

## 🔍 Zweck des Audit-Trail Systems

### **Ziele:**
- **Nachvollziehbarkeit**: Warum hat das System welche Entscheidung getroffen?
- **Debugging**: Bei Fehlern/Verlusten Ursache identifizieren
- **Optimierung**: Erfolgreiche vs. schlechte Entscheidungen analysieren
- **Eigenverantwortung**: Kontrolle über automatisierte Trades behalten

## 📊 **Trading-Entscheidungen dokumentieren**

### **Vollständige Trade-Dokumentation:**
```yaml
trade_log_structure:
  transaction_id: "unique_identifier"
  timestamp: "2024-01-15T10:30:00Z"
  symbol: "AAPL"
  action: "buy|sell|hold"
  quantity: 5
  price: 150.25
  total_amount: 751.25
  fees: 1.25
  
  decision_context:
    ml_score: 0.75
    confidence_level: "high"
    primary_signals: ["rsi_oversold", "positive_sentiment"]
    market_conditions: "normal_volatility"
    portfolio_impact: "improves_diversification"
    
  risk_assessment:
    position_size_percentage: 7.5
    stop_loss_level: 142.74
    expected_risk: "low"
    correlation_impact: 0.3
```

### **Entscheidungslogik-Trail:**
```yaml
decision_process:
  data_sources_used:
    - "yahoo_finance_ohlcv"
    - "sentiment_analysis" 
    - "technical_indicators"
    
  analysis_steps:
    1: "data_collection_completed"
    2: "technical_analysis_performed" 
    3: "ml_model_prediction_generated"
    4: "risk_assessment_completed"
    5: "portfolio_impact_evaluated"
    6: "final_decision_made"
    
  override_factors:
    manual_intervention: false
    risk_limit_override: false
    market_condition_override: false
```

## 🤖 **ML-Entscheidungen nachvollziehen**

### **Feature-Importance Tracking:**
```yaml
ml_decision_log:
  model_version: "xgb_v1.2.3"
  prediction_timestamp: "2024-01-15T10:29:45Z"
  input_features:
    rsi_14: 32.5
    macd_signal: 0.75
    volume_ratio: 1.2
    sentiment_score: 0.6
    price_momentum: 0.15
    
  feature_importance:
    rsi_14: 0.35              # 35% Einfluss
    sentiment_score: 0.25     # 25% Einfluss  
    macd_signal: 0.20         # 20% Einfluss
    volume_ratio: 0.15        # 15% Einfluss
    price_momentum: 0.05      # 5% Einfluss
    
  model_output:
    raw_prediction: 0.751
    confidence_score: 0.85
    recommendation: "strong_buy"
    risk_score: 0.25
```

### **Model-Performance Tracking:**
```yaml
model_performance:
  recent_accuracy: 0.72         # 72% Trefferquote letzte 30 Tage
  precision: 0.68               # 68% Präzision
  recall: 0.75                  # 75% Recall
  sharpe_ratio: 1.2            # Risk-adjusted Performance
  
  prediction_distribution:
    strong_buy: 15              # Anzahl letzte 30 Tage
    buy: 25
    hold: 40
    sell: 12
    strong_sell: 3
```

## 🚨 **System-Events und Fehler**

### **API-Interaktionen protokollieren:**
```yaml
api_event_log:
  timestamp: "2024-01-15T10:30:15Z"
  api_endpoint: "bitpanda_trading_api"
  request_type: "place_order"
  request_payload: "order_details_encrypted"
  
  response:
    status_code: 200
    response_time_ms: 250
    success: true
    order_id: "bp_12345"
    
  error_handling:
    retries_attempted: 0
    fallback_triggered: false
    manual_intervention_required: false
```

### **System-Fehler dokumentieren:**
```yaml
error_event_log:
  error_id: "err_20240115_001"
  timestamp: "2024-01-15T10:31:00Z"
  error_type: "data_source_timeout"
  severity: "medium"
  
  error_details:
    component: "yahoo_finance_plugin"
    function: "fetch_ohlcv_data"
    symbol: "MSFT"
    timeout_duration: 30
    
  impact_assessment:
    trading_halted: false
    fallback_data_used: true
    user_notification: true
    
  resolution:
    auto_recovery: true
    recovery_time_seconds: 45
    manual_action_required: false
```

### **Fallback-Mechanismen:**
```yaml
fallback_events:
  trigger: "primary_data_source_failed"
  fallback_action: "use_cached_data"
  fallback_duration: 300       # 5 Minuten
  
  data_quality_check:
    cache_age_minutes: 15
    data_completeness: 0.95
    acceptable_for_trading: true
    
  monitoring:
    primary_source_recovery_check: 60  # Alle 60s prüfen
    max_fallback_duration: 1800        # Max 30 Min Fallback
    escalation_threshold: 900          # Nach 15 Min eskalieren
```

## 📈 **Reporting & Analyse-Tools**

### **Performance-Analyse:**
```yaml
performance_tracking:
  daily_summary:
    date: "2024-01-15"
    trades_executed: 3
    total_pnl: -5.25
    best_trade: +12.50
    worst_trade: -8.75
    success_rate: 0.67
    
  weekly_analysis:
    week_ending: "2024-01-14"
    total_trades: 15
    winning_trades: 9
    losing_trades: 6
    gross_profit: 125.00
    gross_loss: -89.50
    net_profit: 35.50
    max_drawdown: -15.25
    
  model_performance:
    prediction_accuracy: 0.72
    false_positives: 4
    false_negatives: 3
    model_drift_detected: false
```

### **Audit-Reports:**
```yaml
audit_report_generation:
  daily_activity_report:
    trades_summary: true
    risk_events: true
    system_health: true
    compliance_status: true
    
  weekly_compliance_check:
    position_limits_compliance: true
    trading_frequency_compliance: true
    risk_management_effectiveness: true
    error_rate_analysis: true
    
  monthly_performance_review:
    roi_analysis: true
    benchmark_comparison: true
    model_performance_evaluation: true
    recommendation_accuracy: true
```

## 🗄️ **Strukturierte Datenarchivierung**

### **Log-Datei Struktur:**
```
/opt/da-ki/logs/
├── trading/
│   ├── trades_2024_01.jsonl          # Monatliche Trade-Logs
│   ├── decisions_2024_01.jsonl       # ML-Entscheidungen
│   └── performance_2024_01.jsonl     # Performance-Metriken
├── system/
│   ├── api_calls_2024_01_15.log     # Tägliche API-Logs
│   ├── errors_2024_01_15.log        # Fehler-Logs
│   └── events_2024_01_15.log        # System-Events
├── audit/
│   ├── compliance_2024_01.log       # Compliance-Events
│   ├── risk_events_2024_01.log      # Risiko-Events
│   └── manual_interventions.log     # Manuelle Eingriffe
└── analytics/
    ├── daily_summary_2024_01_15.json
    ├── weekly_report_2024_w03.json
    └── monthly_analysis_2024_01.json
```

### **Strukturierte Log-Formate:**
```json
// Beispiel Trade-Log Entry
{
  "timestamp": "2024-01-15T10:30:00Z",
  "event_type": "trade_executed",
  "trade_id": "t_20240115_001",
  "symbol": "AAPL",
  "action": "buy",
  "quantity": 5,
  "price": 150.25,
  "ml_score": 0.75,
  "risk_score": 0.25,
  "decision_factors": ["rsi_oversold", "positive_sentiment"],
  "compliance_check": "passed",
  "execution_status": "success"
}
```

## 🔧 **Implementierungs-Konfiguration**

### **Audit-Trail Settings in config.yaml:**
```yaml
audit_trail:
  logging_enabled: true
  log_trading_decisions: true
  log_ml_decisions: true
  log_system_events: true
  structured_logging: true
  retention_days: 365
  
  log_levels:
    trading: "INFO"
    ml_decisions: "DEBUG"
    system_events: "INFO" 
    errors: "ERROR"
    
  export_formats:
    json: true                # Für programmatische Analyse
    csv: true                 # Für Excel/Spreadsheet
    human_readable: true      # Für manuelle Review
```

### **Monitoring & Alerting:**
```yaml
audit_monitoring:
  daily_log_rotation: true
  log_size_monitoring: true
  missing_data_alerts: true
  pattern_anomaly_detection: true
  
  alert_conditions:
    high_error_rate: 10       # >10 Fehler/Stunde
    missing_trade_logs: true  # Fehlende Trade-Dokumentation  
    model_drift: 0.15         # >15% Performance-Abfall
    compliance_violations: 1   # Jede Compliance-Verletzung
```

## 📊 **Analyse-Dashboard Integration**

### **Real-time Monitoring:**
- **Live Trading-Status**: Aktuelle Positionen und PnL
- **Model Performance**: Live Accuracy und Confidence
- **Risk Metrics**: Aktuelle Exposure und Limits
- **System Health**: API-Status und Fehlerrate

### **Historical Analysis:**
- **Trade Performance**: Erfolgsrate über Zeit
- **Model Evolution**: Performance-Trends der ML-Modelle
- **Risk Events**: Häufigkeit und Impact von Risiko-Events
- **Compliance Tracking**: Einhaltung aller Limits und Regeln