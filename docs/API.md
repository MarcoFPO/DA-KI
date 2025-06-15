# 🚀 DA-KI API Dokumentation

## 📋 Übersicht

Die DA-KI API ist eine moderne RESTful API, die mit FastAPI entwickelt wurde und umfassende Funktionalitäten für Aktienanalyse, KI-Wachstumsprognosen und Live-Portfolio-Monitoring bietet.

**Base URL**: `http://10.1.1.110:8003`  
**API Version**: v2.0  
**Format**: JSON  
**Authentication**: Bearer Token (geplant)

## 🔗 Quick Links

- **Interactive API Docs**: http://10.1.1.110:8003/docs (Swagger UI)
- **Alternative Docs**: http://10.1.1.110:8003/redoc (ReDoc)
- **OpenAPI Schema**: http://10.1.1.110:8003/openapi.json

## 📊 API Endpoints Übersicht

| Kategorie | Endpoint | Methode | Beschreibung | Status |
|-----------|----------|---------|--------------|---------|
| **Health** | `/health` | GET | Service Health Check | ✅ |
| **Growth** | `/api/wachstumsprognose/top10` | GET | Top 10 Wachstumsaktien | ✅ |
| **Monitoring** | `/api/live-monitoring/add` | POST | Position hinzufügen | ✅ |
| **Monitoring** | `/api/monitoring/summary` | GET | Portfolio-Übersicht | ✅ |
| **Search** | `/api/aktien-suche/{symbol}` | GET | Aktien-Details suchen | ✅ |
| **News** | `/api/markt-nachrichten` | GET | Aktuelle Marktnachrichten | ✅ |
| **Trends** | `/api/aktien-trends` | GET | Trending Aktien | ✅ |

## 🤖 KI-Wachstumsprognose Endpoints

### GET /api/wachstumsprognose/top10

Ruft die Top 10 Wachstumsaktien basierend auf dem 5-Faktor KI-Scoring-System ab.

**Request:**
```http
GET /api/wachstumsprognose/top10
Accept: application/json
```

**Response:**
```json
{
  "top_10_wachstums_aktien": [
    {
      "symbol": "NVDA",
      "name": "NVIDIA Corporation",
      "wachstums_score": 95.8,
      "current_price": 925.30,
      "branche": "Technology",
      "hauptsitz": "Santa Clara, CA",
      "wkn": "918422",
      "isin": "US67066G1040",
      "prognose_30_tage": {
        "prognostizierter_preis": 1050.00,
        "erwartete_rendite_prozent": 13.5,
        "vertrauen_level": "Hoch",
        "risiko_level": "Mittel"
      }
    }
  ],
  "cache_status": "fresh",
  "nächste_aktualisierung": "2025-06-14T09:30:00",
  "berechnet_am": "2025-06-14T08:30:00"
}
```

**Response Codes:**
- `200`: Erfolgreich
- `202`: Berechnung läuft (Background Task)
- `500`: Server Error

**Caching:**
- Cache Duration: 1 Stunde
- Background Refresh: Automatisch

---

## 📊 Live-Monitoring Endpoints

### POST /api/live-monitoring/add

Fügt eine neue Position zum Live-Monitoring hinzu mit detailliertem Position-Tracking.

**Request:**
```http
POST /api/live-monitoring/add
Content-Type: application/json

{
  "symbol": "AAPL",
  "shares": 10,
  "investment": 1500.00
}
```

**Request Body Schema:**
```json
{
  "symbol": {
    "type": "string",
    "pattern": "^[A-Z]{1,5}$",
    "description": "Stock symbol (1-5 uppercase letters)",
    "example": "AAPL"
  },
  "shares": {
    "type": "integer",
    "minimum": 1,
    "maximum": 10000,
    "description": "Number of shares to monitor"
  },
  "investment": {
    "type": "number",
    "minimum": 0.01,
    "maximum": 1000000,
    "description": "Total investment amount in EUR"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Position für AAPL erfolgreich hinzugefügt",
  "position_id": 1,
  "details": {
    "symbol": "AAPL",
    "shares": 10,
    "investment_amount": 1500.00,
    "entry_price": 195.89,
    "current_value": 1958.90
  },
  "created_at": "2025-06-14T08:33:29.110530"
}
```

**Response Codes:**
- `201`: Position erfolgreich erstellt
- `400`: Ungültige Request-Daten
- `409`: Position bereits vorhanden
- `500`: Server Error

---

### GET /api/monitoring/summary

Ruft eine Zusammenfassung aller Live-Monitoring Positionen ab mit aktuellen Gewinn/Verlust-Berechnungen.

**Request:**
```http
GET /api/monitoring/summary
Accept: application/json
```

**Response:**
```json
{
  "stocks": [
    {
      "symbol": "AAPL",
      "shares": 10,
      "investment_amount": 1500.00,
      "entry_price": 195.89,
      "current_price": 198.50,
      "total_value": 1985.00,
      "profit_loss": 485.00,
      "change_percent": 32.33,
      "added_at": "2025-06-14 08:33:29"
    }
  ],
  "total_positions": 1,
  "total_investment": 1500.00,
  "total_current_value": 1985.00,
  "total_profit_loss": 485.00,
  "portfolio_return_percent": 32.33,
  "last_updated": "2025-06-14T08:45:00"
}
```

**Response Codes:**
- `200`: Erfolgreich
- `500`: Server Error

**Auto-Update:**
- Update-Intervall: 60 Sekunden
- Preis-Aktualisierung: Real-time via External APIs

---

## 🔍 Aktien-Suche Endpoints

### GET /api/aktien-suche/{symbol}

Sucht detaillierte Informationen zu einer spezifischen Aktie.

**Request:**
```http
GET /api/aktien-suche/AAPL
Accept: application/json
```

**Path Parameters:**
- `symbol` (string): Aktien-Symbol (z.B. "AAPL", "TSLA")

**Response:**
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "current_price": 195.89,
  "change": "+2.34",
  "change_percent": "+1.21%",
  "market_cap": "3.0T",
  "pe_ratio": "29.8",
  "volume": "45.2M",
  "52_week_high": 199.62,
  "52_week_low": 164.08,
  "news": [
    {
      "title": "Apple stellt neue KI-Features vor",
      "snippet": "Apple Intelligence revolutioniert mobile AI-Erfahrungen.",
      "source": "Tech News Daily",
      "date": "2025-06-14",
      "url": "https://example.com/news/apple-ai"
    }
  ]
}
```

**Response Codes:**
- `200`: Aktie gefunden
- `404`: Aktie nicht gefunden
- `500`: Server Error

---

## 📰 Marktdaten Endpoints

### GET /api/markt-nachrichten

Ruft aktuelle Marktnachrichten und Trends ab.

**Request:**
```http
GET /api/markt-nachrichten
Accept: application/json
```

**Response:**
```json
{
  "nachrichten": [
    {
      "titel": "KI-Aktien erreichen neue Höchststände",
      "zusammenfassung": "Künstliche Intelligenz treibt Technologieaktien auf neue Rekordniveaus.",
      "quelle": "Tech Investor",
      "datum": "2025-06-14",
      "kategorie": "Technologie",
      "relevanz_score": 0.95
    }
  ],
  "anzahl": 10,
  "letztes_update": "2025-06-14T08:30:00"
}
```

---

### GET /api/aktien-trends

Ruft trending Aktien basierend auf Suchvolumen und Handelsaktivität ab.

**Request:**
```http
GET /api/aktien-trends
Accept: application/json
```

**Response:**
```json
{
  "trends": [
    {
      "symbol": "NVDA",
      "name": "NVIDIA Corp.",
      "trend_score": 98,
      "veränderung": "+8.7%",
      "volumen": "Sehr Hoch",
      "grund": "KI-Chip Durchbruch"
    }
  ],
  "aktualisiert": "2025-06-14T08:30:00",
  "basis": "Google Trends + Handelsvolumen"
}
```

---

## 🔧 Administrative Endpoints

### GET /health

Service Health Check für Monitoring und Load Balancer.

**Request:**
```http
GET /health
Accept: application/json
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-14T08:30:00",
  "version": "2.0.0",
  "services": {
    "database": "connected",
    "external_apis": "operational",
    "cache": "operational"
  },
  "uptime_seconds": 3600
}
```

---

## 🚨 Error Handling

### Standard Error Response

Alle API-Fehler folgen einem konsistenten Format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "shares",
      "issue": "Value must be greater than 0"
    },
    "timestamp": "2025-06-14T08:30:00",
    "request_id": "uuid-1234-5678"
  }
}
```

### Error Codes

| HTTP Code | Error Type | Beschreibung |
|-----------|------------|-------------|
| `400` | Bad Request | Ungültige Request-Parameter |
| `401` | Unauthorized | Authentication erforderlich |
| `403` | Forbidden | Zugriff verweigert |
| `404` | Not Found | Ressource nicht gefunden |
| `409` | Conflict | Ressourcen-Konflikt |
| `422` | Unprocessable Entity | Validierungsfehler |
| `429` | Too Many Requests | Rate Limit überschritten |
| `500` | Internal Server Error | Server-Fehler |
| `503` | Service Unavailable | Service temporarily down |

---

## 📏 Rate Limiting

**Current Limits:**
- 100 requests per minute per IP
- 1000 requests per hour per IP
- Burst allowance: 20 requests

**Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1638360000
X-RateLimit-Retry-After: 60
```

---

## 🔐 Authentication (Geplant)

### Bearer Token Authentication

```http
Authorization: Bearer <JWT_TOKEN>
```

### API Key Authentication

```http
X-API-Key: <API_KEY>
```

### OAuth 2.0 Flow

```http
# Authorization Endpoint
GET /oauth/authorize?client_id=...&response_type=code&scope=read+write

# Token Endpoint  
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&code=...&client_id=...&client_secret=...
```

---

## 📊 Request/Response Examples

### Kompletter Workflow: Position hinzufügen

**1. Wachstumsprognose abrufen:**
```bash
curl -X GET "http://10.1.1.110:8003/api/wachstumsprognose/top10" \
  -H "Accept: application/json"
```

**2. Position hinzufügen:**
```bash
curl -X POST "http://10.1.1.110:8003/api/live-monitoring/add" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "NVDA",
    "shares": 5,
    "investment": 4500.00
  }'
```

**3. Portfolio-Status prüfen:**
```bash
curl -X GET "http://10.1.1.110:8003/api/monitoring/summary" \
  -H "Accept: application/json"
```

---

## 🔄 WebSocket Endpoints (Geplant)

### Real-time Portfolio Updates

```javascript
// WebSocket Connection
const ws = new WebSocket('ws://10.1.1.110:8003/ws/live-monitoring');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Real-time update:', data);
};

// Message Format
{
  "type": "portfolio_update",
  "data": {
    "total_value": 15750.00,
    "profit_loss": 1250.00,
    "positions": [...]
  },
  "timestamp": "2025-06-14T08:30:00"
}
```

---

## 📋 API Versioning

### Current Version Strategy

```http
# Default (Current Version)
GET /api/wachstumsprognose/top10

# Explicit Versioning  
GET /api/v2/wachstumsprognose/top10

# Legacy Support
GET /api/v1/growth-predictions  # Deprecated
```

### Version Headers

```http
Accept: application/vnd.da-ki.v2+json
API-Version: 2.0
```

---

## 🧪 Testing

### API Testing mit curl

```bash
# Health Check
curl http://10.1.1.110:8003/health

# Get Top 10 Wachstumsaktien
curl http://10.1.1.110:8003/api/wachstumsprognose/top10

# Add Position
curl -X POST http://10.1.1.110:8003/api/live-monitoring/add \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","shares":10,"investment":1500}'

# Get Portfolio Summary
curl http://10.1.1.110:8003/api/monitoring/summary
```

### Automated Testing

```python
import requests
import pytest

class TestDAKIAPI:
    base_url = "http://10.1.1.110:8003"
    
    def test_health_endpoint(self):
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_add_position(self):
        data = {
            "symbol": "AAPL",
            "shares": 10,
            "investment": 1500.00
        }
        response = requests.post(f"{self.base_url}/api/live-monitoring/add", json=data)
        assert response.status_code == 201
        assert "position_id" in response.json()
```

---

## 📈 Performance Considerations

### Response Times (Target)
- Health Check: < 50ms
- Cached Data: < 200ms
- Database Queries: < 500ms
- External API Calls: < 2000ms

### Optimization Strategies
- **Caching**: Redis für häufig abgerufene Daten
- **Async Processing**: Background Tasks für schwere Berechnungen
- **Database Indexing**: Optimierte Queries
- **Connection Pooling**: Effiziente DB-Verbindungen

---

## 📋 Changelog

### Version 2.0.0 (2025-06-14)
- ✅ Enhanced Live-Monitoring mit Position-Tracking
- ✅ Neue `/api/live-monitoring/add` Endpoint
- ✅ Erweiterte `/api/monitoring/summary` mit Profit/Loss
- ✅ Verbesserte Error Handling
- ✅ Rate Limiting Implementation

### Version 1.0.0 (2025-06-13)
- ✅ Initial API Implementation
- ✅ Basis Wachstumsprognose Endpoints
- ✅ SQLite Integration
- ✅ FastAPI Framework Setup

---

**📚 API Dokumentation | Version 2.0 | DA-KI Project**

*Entwickelt mit [Claude Code](https://claude.ai/code) - Moderne KI-gestützte Softwareentwicklung*

**Nützliche Links:**
- [Interactive API Docs](http://10.1.1.110:8003/docs)
- [GitHub Repository](https://github.com/MarcoFPO/DA-KI)
- [Architektur-Dokumentation](./ARCHITECTURE.md)