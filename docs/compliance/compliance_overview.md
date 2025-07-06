# DA-KI Compliance & Regulierung - Übersicht

## 🏛️ Rechtlicher Rahmen für privates Trading-System

### **Grundsätzliche Einordnung:**
DA-KI ist ein **privates Handelssystem** für Eigengebrauch - nicht kommerziell, nicht für Dritte, keine Finanzdienstleistung.

## 📋 **Compliance-Bereiche (Abgeschlossen)**

### **7.1 Rechtlicher Rahmen ✅**

#### **A) Rechtliche Abgrenzungen:**
- **Privater Eigenhandel**: Keine MiFID II/WpHG Anwendung
- **Automatisierungsgrad**: Vollautomatisch erlaubt für Eigengebrauch
- **Verlustrisiko**: Vollständige Eigenverantwortung
- **System-Limits**: Konfigurierbar in config.yaml

#### **B) Haftungsfragen:**
- **Systemfehler**: Vollständige Eigenverantwortung
- **API-Ausfälle**: Eigenes Risiko, Fallback-Strategien implementiert
- **Datenverlust**: Eigene Verantwortung, Proxmox Backup extern
- **Trading-Verluste**: Eigenes Risiko mit Stop-Loss Mechanismen

### **7.4 Audit-Trail & Nachvollziehbarkeit ✅**
- **Trading-Entscheidungen dokumentieren**: Jeder Trade mit Begründung
- **ML-Entscheidungen nachvollziehen**: Feature-Importance, Confidence-Scores
- **System-Events und Fehler**: Vollständiges Logging
- **Reporting & Analyse-Tools**: Performance-Tracking, Success-Rate

### **7.5 Broker-spezifische Compliance ✅**
- **Rate-Limits**: Externe API-Limits von Bitpanda/One Trading beachten
- **Technische Beschränkungen**: Min/Max Order-Größen, Trading-Zeiten
- **Fehlerbehandlung**: Graceful Degradation bei API-Ausfällen

### **7.6 Risiko-Management & Verlustbegrenzung ✅**
- **Stop-Loss-Mechanismen**: Position- und Portfolio-Level
- **Position-Limits**: Konfigurierbare Einzel- und Gesamtlimits
- **Trading-Frequenz**: Begrenzte Trades pro Zeitraum
- **Marktrisiko-Kontrollen**: Volatilitäts- und Liquiditäts-Filter
- **Rechtliche Absicherung**: Dokumentierte Eigenverantwortung

## ❌ **Nicht relevante Bereiche (Gestrichen)**
- **~~7.2 Steuerrechtliche Anforderungen~~**: Durch Broker abgedeckt
- **~~7.3 Datenschutz (DSGVO)~~**: Nur eigene Daten, eigenes Risiko

## ⚙️ **Implementierungs-Anforderungen**

### **Konfigurationsmanagement:**
Alle Compliance-relevanten Grenzwerte müssen in `config.yaml` ausgelagert werden:

```yaml
compliance:
  private_trading_limits:
    max_daily_trades: 5
    max_single_position: 200.00
    max_total_investment: 1000.00
    automatic_stop_loss_percentage: 5.0
    
  legal_framework:
    trading_purpose: "private_investment"
    system_type: "experimental_tool"
    user_status: "private_individual"
    regulatory_status: "non_professional"
    
  risk_management:
    manual_override_available: true
    mandatory_review_interval: "daily"
    emergency_stop_enabled: true
    loss_notification_threshold: 100.00

broker_limits:
  bitpanda:
    rate_limit_per_minute: 100
    min_order_size: 25.00
    max_order_size: 1000.00
    trading_hours: "09:00-17:30"
```

### **Logging-Anforderungen:**
```
/opt/da-ki/logs/
├── trading.log          # Alle Trading-Entscheidungen
├── decisions.log        # ML-Entscheidungen mit Scores  
├── api_calls.log        # Broker-API Interaktionen
├── data_sources.log     # Marktdaten-Abrufe
└── audit.log           # System-Changes & Admin-Actions
```

## ✅ **Compliance-Status**
**VOLLSTÄNDIG GEPLANT** - Alle relevanten Bereiche für privaten Eigenhandel abgedeckt.

**Rechtlicher Hinweis**: Diese Planung basiert auf privatem Eigengebrauch. Bei Änderung des Nutzungsumfangs sind zusätzliche rechtliche Prüfungen erforderlich.