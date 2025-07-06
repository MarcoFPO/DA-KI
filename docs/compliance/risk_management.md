# Risiko-Management & Verlustbegrenzung

## 🛡️ Übersicht Risiko-Management System

### **Ziele:**
- **Kapitalschutz**: Begrenzte Verluste bei automatisiertem Trading
- **Systemfehler-Schutz**: Absicherung gegen Bugs/Fehlfunktionen  
- **Marktrisiko-Minimierung**: Schutz vor extremen Marktbewegungen
- **Rechtliche Absicherung**: Dokumentierte Eigenverantwortung

## 🎯 **Stop-Loss-Mechanismen**

### **Position-Level Stop-Loss:**
```yaml
position_stop_loss:
  automatic_percentage: 5.0        # 5% Verlust-Stopp pro Position
  manual_override: true            # Manuelle Anpassung möglich
  trailing_stop: false             # Vereinfacht: Fixer Stop-Loss
  implementation: "broker_side"    # Via Broker-API
```

### **Portfolio-Level Stop-Loss:**
```yaml
portfolio_stop_loss:
  daily_loss_limit: 50.00         # Max €50 Verlust pro Tag
  total_loss_limit: 100.00        # Emergency-Stop bei €100 Gesamtverlust
  cool_down_period: "24_hours"    # 24h Pause nach Verlust-Limit
  alert_threshold: 25.00          # Warnung bei €25 Verlust
```

### **Emergency-Stop:**
```yaml
emergency_mechanisms:
  manual_stop_button: true        # Sofort-Stopp verfügbar
  system_error_stop: true         # Auto-Stopp bei kritischen Fehlern
  api_failure_stop: true          # Stopp bei Broker-API Problemen
  volatility_stop: true           # Stopp bei extremer Markt-Volatilität
```

## 📊 **Position-Limits & Diversifikation**

### **Einzelposition-Limits:**
```yaml
position_limits:
  max_single_position: 200.00     # Max €200 pro Aktie
  max_sector_exposure: 400.00     # Max €400 pro Sektor
  max_positions_total: 10         # Max 10 verschiedene Aktien
  min_position_size: 25.00        # Min €25 (Broker-Limit)
```

### **Portfolio-Zusammensetzung:**
```yaml
diversification:
  max_portfolio_value: 1000.00    # Gesamt-Investment-Limit
  min_cash_reserve: 100.00        # Mindest-Liquidität
  max_growth_stocks: 60           # Max 60% Wachstumsaktien
  max_single_market: 70           # Max 70% ein einzelner Markt (DE/US)
```

### **Sektor-Diversifikation:**
```yaml
sector_limits:
  technology: 30                   # Max 30% Tech-Aktien
  healthcare: 25                   # Max 25% Pharma/Health
  finance: 20                      # Max 20% Finanzsektor
  energy: 15                       # Max 15% Energie
  other: 10                        # Max 10% sonstige Sektoren
```

## ⏰ **Trading-Frequenz Kontrolle**

### **Zeitbasierte Limits:**
```yaml
frequency_limits:
  max_trades_per_day: 5           # Höchstens 5 Trades täglich
  max_trades_per_week: 15         # Höchstens 15 Trades wöchentlich
  max_trades_per_month: 50        # Höchstens 50 Trades monatlich
  min_time_between_trades: 3600   # Min 1h zwischen Trades
```

### **Cooling-Off Perioden:**
```yaml
cooling_periods:
  after_loss: "24_hours"          # 24h Pause nach Verlust
  after_error: "12_hours"         # 12h Pause nach System-Fehler
  after_daily_limit: "until_next_day"  # Pause bis nächster Tag
  weekend_pause: true             # Kein Trading am Wochenende
```

### **Vermeidung Panic-Trading:**
```yaml
panic_prevention:
  max_same_day_sells: 2           # Max 2 Verkäufe am selben Tag
  min_holding_period: 3           # Min 3 Tage Haltedauer
  no_revenge_trading: true        # Kein sofortiges Re-Investment nach Verlust
  volatility_threshold: 10        # Stopp bei >10% Tages-Volatilität
```

## 📈 **Marktrisiko-Kontrollen**

### **Volatilitäts-Filter:**
```yaml
volatility_controls:
  max_daily_volatility: 10.0      # Kein Trading bei >10% Tages-Schwankung
  vix_threshold: 30               # Stopp bei VIX >30 (Angst-Index)
  market_hours_only: true         # Nur während Börsenzeiten
  no_earnings_days: true          # Kein Trading an Earnings-Tagen
```

### **Liquiditäts-Checks:**
```yaml
liquidity_requirements:
  min_daily_volume: 1000000       # Min €1M Tagesvolumen
  min_market_cap: 1000000000      # Min €1Mrd Marktkapitalisierung
  major_indices_only: true       # Nur DAX/MDAX/S&P500 Aktien
  no_penny_stocks: true           # Keine Aktien <€5
```

### **Marktphasen-Erkennung:**
```yaml
market_phase_controls:
  bear_market_reduction: 50       # 50% weniger Trading in Bärenmärkten
  recession_indicators: true      # Stopp bei Rezessions-Signalen
  correlation_monitoring: true    # Überwachung Asset-Korrelationen
  systematic_risk_check: true     # Check auf Systemrisiken
```

## 🔧 **Technische Implementierung**

### **Risk-Engine Integration:**
```python
class RiskManager:
    def __init__(self, config):
        self.limits = config['compliance']['private_trading_limits']
        self.risk_settings = config['compliance']['risk_management']
        
    def validate_trade(self, trade_request):
        """Prüfe alle Risiko-Limits vor Trade-Ausführung"""
        checks = [
            self.check_position_limits(trade_request),
            self.check_daily_limits(),
            self.check_portfolio_exposure(trade_request),
            self.check_market_conditions(),
            self.check_volatility_filters()
        ]
        return all(checks)
        
    def emergency_stop(self, reason):
        """Sofortiger Handelsstopp mit Begründung"""
        self.trading_enabled = False
        self.log_emergency_stop(reason)
        self.alert_user(reason)
```

### **Monitoring & Alerts:**
```yaml
risk_monitoring:
  real_time_checks: true          # Kontinuierliche Überwachung
  daily_risk_report: true         # Täglicher Risiko-Bericht
  loss_alerts: true               # Sofortige Verlust-Benachrichtigung
  limit_warnings: true            # Warnung bei Annäherung an Limits
  
alert_channels:
  email_alerts: false             # Keine E-Mail (privat)
  log_alerts: true                # Logging aller Alerts
  system_notifications: true     # System-interne Benachrichtigungen
  dashboard_warnings: true       # GUI-Warnungen
```

## 📋 **Compliance & Dokumentation**

### **Rechtliche Absicherung:**
```yaml
legal_documentation:
  risk_acceptance: "documented"    # Risiko-Akzeptanz dokumentiert
  system_limits: "enforced"       # System-Grenzen durchgesetzt
  manual_override: "available"    # Manuelle Kontrolle möglich
  loss_responsibility: "personal" # Persönliche Verlust-Verantwortung
```

### **Audit-Trail für Risiko-Events:**
```yaml
risk_logging:
  all_limit_breaches: true        # Alle Limit-Überschreitungen
  stop_loss_triggers: true        # Stop-Loss Auslösungen
  emergency_stops: true           # Emergency-Stop Events
  manual_overrides: true          # Manuelle Eingriffe
  risk_score_changes: true        # Risiko-Score Änderungen
```

## ⚖️ **Konfigurierbare Parameter**

Alle Risiko-Parameter sind in `config.yaml` konfigurierbar:

```yaml
# Beispiel-Anpassung für konservativeren Ansatz:
compliance:
  private_trading_limits:
    max_single_position: 100.00   # Reduziert von €200
    automatic_stop_loss_percentage: 3.0  # Reduziert von 5%
    max_daily_trades: 3           # Reduziert von 5
```

## 🎯 **Risiko-Management Ziele**

### **Kurzfristig (1-3 Monate):**
- Keine einzelnen Verluste >€10
- Maximaler Monats-Verlust: €50
- System-Stabilität: 99% Uptime

### **Mittelfristig (3-12 Monate):**
- Drawdown <10% des Portfolios
- Positive Risk-Adjusted Returns
- Erfolgreiche Verlust-Begrenzung

### **Langfristig (>1 Jahr):**
- Kapitalerhalt als Minimum-Ziel
- Moderate Wertsteigerung bei kontrolliertem Risiko
- Bewährte Risiko-Management Strategien