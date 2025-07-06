# Broker-spezifische Compliance

## 🏦 Broker-Integration Übersicht

### **Primärer Broker: Bitpanda**
- **Regulierung**: EU-reguliert (Österreich/Deutschland)
- **API-Zugang**: RESTful API für automatisierten Handel
- **Asset-Klassen**: Aktien, ETFs, Kryptowährungen
- **Compliance-Status**: Vollständig reguliert und lizenziert

### **Alternative: One Trading**
- **Regulierung**: EU-reguliert (Österreich)
- **API-Zugang**: RESTful API verfügbar
- **Fokus**: Aktien und ETFs
- **Backup-Option**: Falls Bitpanda API nicht verfügbar

## 📊 **Rate-Limits und technische Beschränkungen**

### **Bitpanda API-Limits (externe Vorgaben):**

#### **Request-Rate-Limits:**
```yaml
bitpanda_api_limits:
  rest_api:
    requests_per_minute: 100      # Von Bitpanda vorgegeben
    requests_per_hour: 1000       # Stündliches Limit
    burst_limit: 10               # Max 10 Requests in 10 Sekunden
    
  trading_api:
    orders_per_minute: 20         # Order-spezifisches Limit
    orders_per_day: 500           # Tägliches Order-Limit
    concurrent_orders: 10         # Gleichzeitige offene Orders
    
  market_data:
    price_requests_per_minute: 200  # Kursdaten-Abfragen
    historical_data_per_hour: 50    # Historische Daten
```

#### **Order-Beschränkungen (Bitpanda-seitig):**
```yaml
order_constraints:
  minimum_order_sizes:
    stocks: 25.00                 # Min €25 pro Aktien-Order
    etfs: 25.00                   # Min €25 pro ETF-Order
    
  maximum_order_sizes:
    per_order: 10000.00           # Max €10.000 pro Order
    daily_volume: 50000.00        # Max €50.000 tägliches Volumen
    
  price_limits:
    max_deviation_from_market: 10 # Max 10% Abweichung vom Marktpreis
    limit_order_duration: 30      # Limit-Orders verfallen nach 30 Tagen
    
  order_types:
    supported: ["market", "limit", "stop_loss"]
    not_supported: ["trailing_stop", "iceberg"]
```

#### **Trading-Zeiten (marktabhängig):**
```yaml
trading_hours:
  german_markets:
    xetra: "09:00-17:30 CET"      # XETRA Haupthandelszeit
    frankfurt: "08:00-22:00 CET"  # Frankfurter Börse erweitert
    
  us_markets:
    nyse: "15:30-22:00 CET"       # NYSE in deutscher Zeit
    nasdaq: "15:30-22:00 CET"     # NASDAQ in deutscher Zeit
    
  restrictions:
    weekends: "no_trading"        # Keine Trades am Wochenende
    holidays: "market_dependent"   # Je nach Börsen-Feiertagen
    maintenance: "api_announcements" # Wartungszeiten werden angekündigt
```

#### **Technische API-Limits:**
```yaml
technical_constraints:
  connection:
    timeout: 30                   # 30 Sekunden Request-Timeout
    keep_alive: 300               # 5 Minuten Connection-Keep-Alive
    max_connections: 5            # Max 5 gleichzeitige Verbindungen
    
  authentication:
    token_lifetime: 3600          # API-Token 1 Stunde gültig
    refresh_threshold: 300        # Token 5 Min vor Ablauf erneuern
    max_auth_attempts: 3          # Max 3 Login-Versuche
    
  data_formats:
    max_request_size: "1MB"       # Maximale Request-Größe
    response_format: "JSON"       # Nur JSON-Responses
    charset: "UTF-8"              # Unicode-Unterstützung
```

## 🔧 **DA-KI Anpassung an Broker-Limits**

### **Rate-Limiting Implementation:**
```python
class BrokerRateLimiter:
    def __init__(self, config):
        self.limits = config['broker_limits']['bitpanda']
        self.request_history = []
        
    async def check_rate_limit(self, request_type):
        """Prüfe Rate-Limits vor API-Aufruf"""
        current_minute_requests = self.count_recent_requests(60)
        
        if current_minute_requests >= self.limits['rate_limit_per_minute']:
            wait_time = self.calculate_wait_time()
            await asyncio.sleep(wait_time)
            
        return self.can_make_request(request_type)
```

### **Order-Validation:**
```python
class OrderValidator:
    def __init__(self, broker_limits):
        self.limits = broker_limits
        
    def validate_order(self, order):
        """Validiere Order gegen Broker-Constraints"""
        checks = [
            self.check_minimum_size(order),
            self.check_maximum_size(order), 
            self.check_price_deviation(order),
            self.check_trading_hours(order),
            self.check_daily_volume_limit(order)
        ]
        return all(checks)
```

### **Fallback-Strategien:**
```yaml
api_fallback_strategy:
  rate_limit_exceeded:
    action: "queue_request"
    retry_after: "wait_for_rate_limit_reset"
    max_queue_size: 10
    
  connection_timeout:
    action: "retry_with_exponential_backoff"
    max_retries: 3
    base_delay: 1
    max_delay: 60
    
  order_rejected:
    action: "log_and_alert"
    retry_logic: "check_rejection_reason"
    manual_review: true
    
  api_maintenance:
    action: "graceful_degradation"
    mode: "read_only"
    alert_user: true
```

## 🛡️ **Fehlerbehandlung & Monitoring**

### **API-Error-Handling:**
```yaml
error_handling:
  http_errors:
    400: "bad_request - validate_input_parameters"
    401: "unauthorized - refresh_authentication_token"
    403: "forbidden - check_api_permissions"
    429: "rate_limited - implement_backoff_strategy"
    500: "server_error - retry_with_delay"
    503: "service_unavailable - switch_to_fallback_mode"
    
  trading_errors:
    insufficient_funds: "reduce_order_size"
    market_closed: "queue_for_next_session"
    invalid_symbol: "validate_symbol_list"
    price_out_of_range: "adjust_limit_price"
```

### **Monitoring & Alerting:**
```yaml
broker_monitoring:
  api_health:
    response_time_threshold: 5000    # >5s Response-Zeit
    error_rate_threshold: 5          # >5% Fehlerrate
    availability_threshold: 99       # <99% Verfügbarkeit
    
  trading_performance:
    order_fill_rate: 95              # <95% Fill-Rate
    execution_delay: 10              # >10s Execution-Delay
    slippage_threshold: 0.5          # >0.5% Slippage
    
  compliance_monitoring:
    rate_limit_violations: 0         # Jede Rate-Limit-Verletzung
    order_rejections: 3              # >3 Rejections/Tag
    api_quota_usage: 80              # >80% Quota-Nutzung
```

### **Logging & Audit-Trail:**
```yaml
broker_logging:
  api_calls:
    log_all_requests: true
    log_all_responses: true
    sanitize_credentials: true       # API-Keys nicht loggen
    include_timing: true
    
  trading_activity:
    order_submissions: true
    order_confirmations: true
    execution_reports: true
    error_responses: true
    
  compliance_events:
    rate_limit_approaches: true      # Bei 80% der Rate-Limits
    large_order_warnings: true       # Orders >€500
    unusual_activity: true           # Ungewöhnliche Patterns
```

## ⚙️ **Konfiguration in config.yaml**

### **Broker-spezifische Einstellungen:**
```yaml
# Bereits in config.yaml enthalten:
broker_limits:
  bitpanda:
    rate_limit_per_minute: 100
    min_order_size: 25.00
    max_order_size: 1000.00
    trading_hours: "09:00-17:30"
    connection_timeout: 30
    max_retries: 3

# Erweiterte Konfiguration:
broker_config:
  primary_broker: "bitpanda"
  fallback_broker: "one_trading"
  
  connection_settings:
    ssl_verify: true
    user_agent: "DA-KI-Trading-Bot/1.0"
    compression: true
    
  order_management:
    default_order_type: "limit"
    price_buffer_percentage: 0.1    # 0.1% Puffer bei Limit-Orders
    order_timeout: 300              # 5 Min Order-Timeout
    
  risk_integration:
    pre_trade_validation: true
    post_trade_verification: true
    position_reconciliation: true
```

## 🔄 **API-Integration Workflow**

### **Standard Trading-Flow:**
```yaml
trading_workflow:
  1_pre_validation:
    - check_rate_limits
    - validate_order_parameters
    - check_account_balance
    - verify_trading_hours
    
  2_order_submission:
    - authenticate_api_connection
    - submit_order_request
    - receive_order_confirmation
    - log_transaction_details
    
  3_execution_monitoring:
    - monitor_order_status
    - track_execution_progress
    - handle_partial_fills
    - process_completion_event
    
  4_post_trade:
    - update_portfolio_positions
    - record_trade_in_database
    - update_risk_metrics
    - generate_audit_trail_entry
```

### **Error-Recovery-Prozess:**
```yaml
error_recovery:
  detection_phase:
    - monitor_api_responses
    - detect_error_patterns
    - classify_error_severity
    - determine_recovery_strategy
    
  recovery_actions:
    - implement_retry_logic
    - switch_to_fallback_data
    - queue_failed_requests
    - alert_system_administrator
    
  verification_phase:
    - confirm_system_recovery
    - validate_data_integrity
    - resume_normal_operations
    - document_incident_details
```

## 📋 **Compliance-Checkliste**

### **Tägliche Checks:**
- [ ] API-Rate-Limits eingehalten
- [ ] Alle Orders erfolgreich übertragen
- [ ] Keine ungewöhnlichen Fehlerrate
- [ ] Trading-Hours befolgt

### **Wöchentliche Reviews:**
- [ ] Broker-API Performance-Analyse
- [ ] Order-Fill-Rate Überprüfung
- [ ] Compliance-Violations Review
- [ ] Fallback-System Tests

### **Monatliche Audits:**
- [ ] Broker-Relationship Status
- [ ] API-Quota-Nutzung Analyse
- [ ] Cost-Benefit-Analyse der API-Nutzung
- [ ] Backup-Broker Bereitschaft prüfen