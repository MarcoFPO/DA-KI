# 🏗️ DA-KI Architektur-Dokumentation

## 📋 Übersicht

DA-KI implementiert eine moderne, modulare Architektur basierend auf dem **Teilprojekt-Konzept** mit klarer Trennung von Verantwortlichkeiten. Die Anwendung folgt einer **Service-orientierten Architektur (SOA)** mit REST-APIs und reaktiven Frontend-Komponenten.

## 🎯 Teilprojekt-Architektur

```mermaid
graph TB
    subgraph "DA-KI Ecosystem"
        CORE[🧠 CORE<br/>Berechnungen & KI]
        FRONTEND[🖥️ FRONTEND<br/>User Interface]
        KI[🤖 KI-WACHSTUMSPROGNOSE<br/>Intelligence Layer]
        LIVE[📊 LIVE-MONITORING<br/>Real-time Operations]
        DEPO[💰 DEPO-STEUERUNG<br/>Portfolio Management]
    end
    
    CORE --> KI
    CORE --> LIVE
    CORE --> DEPO
    FRONTEND --> KI
    FRONTEND --> LIVE
    FRONTEND --> DEPO
    KI <--> LIVE
    LIVE <--> DEPO
```

### Teilprojekt-Details

| Teilprojekt | Verantwortlichkeiten | Technologien | Status |
|-------------|---------------------|--------------|---------|
| **CORE** | Basis-Algorithmen, Datenmodelle, Utils | Python, SQLite, Pandas | ✅ Produktiv |
| **FRONTEND** | UI/UX, Dashboards, User Interactions | Dash, Plotly, HTML/CSS | ✅ Produktiv |
| **KI-WACHSTUMSPROGNOSE** | ML-Modelle, Scoring-Algorithmen | Scikit-learn, NumPy | ✅ Implementiert |
| **LIVE-MONITORING** | Real-time Data, WebSockets | AsyncIO, WebSockets | 🚧 Enhanced |
| **DEPO-STEUERUNG** | Portfolio-Optimierung, Trading | Optimization Libs | 📋 Geplant |

## 🏛️ System-Architektur

### High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        UI[🖥️ Web Dashboard<br/>Dash Frontend]
        API_CLIENT[📱 API Clients<br/>External Integrations]
    end
    
    subgraph "API Layer"
        API[🚀 FastAPI Server<br/>REST Endpoints]
        WS[🔄 WebSocket Handler<br/>Real-time Updates]
    end
    
    subgraph "Service Layer"
        GROWTH[🤖 Growth Prediction<br/>KI-Algorithmen]
        MONITOR[📊 Live Monitoring<br/>Position Tracking]
        PORTFOLIO[💰 Portfolio Service<br/>Optimization]
    end
    
    subgraph "Data Layer"
        DB[(🗄️ SQLite Database<br/>Persistent Storage)]
        CACHE[⚡ Redis Cache<br/>Performance Layer]
        EXT[🌐 External APIs<br/>Market Data]
    end
    
    UI --> API
    API_CLIENT --> API
    API --> WS
    API --> GROWTH
    API --> MONITOR
    API --> PORTFOLIO
    GROWTH --> DB
    MONITOR --> DB
    PORTFOLIO --> DB
    GROWTH --> CACHE
    MONITOR --> CACHE
    MONITOR --> EXT
```

### Component Interaction

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant S as Service
    participant D as Database
    
    U->>F: Klick "Zu Live-Monitoring"
    F->>F: Zeige Position Modal
    U->>F: Eingabe (Aktien, Investment)
    F->>A: POST /api/live-monitoring/add
    A->>S: Verarbeite Position
    S->>D: Speichere Position
    D-->>S: Position ID
    S-->>A: Position Details
    A-->>F: Success Response
    F-->>U: Bestätigung anzeigen
```

## 📁 Datei-Organisation

### Directory Structure

```
DA-KI/
├── 📁 api/                           # API Layer
│   ├── api_top10_final.py           # Haupt-API Server
│   ├── endpoints/                   # Modularisierte Endpoints
│   │   ├── __init__.py
│   │   ├── wachstumsprognose.py    # Growth Prediction APIs
│   │   ├── monitoring.py           # Live Monitoring APIs  
│   │   └── portfolio.py            # Portfolio Management APIs
│   └── middleware/                  # API Middleware
│       ├── auth.py                 # Authentication
│       ├── cache.py                # Caching Layer
│       └── cors.py                 # CORS Configuration
├── 📁 frontend/                     # Frontend Layer
│   ├── dashboard_top10.py          # Haupt-Dashboard
│   ├── components/                 # UI Components
│   │   ├── __init__.py
│   │   ├── growth_cards.py         # Wachstums-Karten
│   │   ├── monitoring_table.py     # Live-Monitoring Tabelle
│   │   ├── portfolio_simulator.py  # Portfolio-Simulation
│   │   └── modals.py               # Modal Dialoge
│   ├── layouts/                    # Layout Templates
│   └── assets/                     # Static Assets (CSS, JS)
├── 📁 services/                     # Service Layer
│   ├── __init__.py
│   ├── growth_prediction_top10.py  # KI-Wachstumsprognose
│   ├── live_monitoring.py          # Live-Monitoring Service
│   ├── portfolio_optimizer.py      # Portfolio-Optimierung
│   ├── data_manager.py             # Datenverarbeitung
│   └── external_apis/              # External API Integrations
│       ├── yahoo_finance.py
│       ├── google_search.py
│       └── market_data.py
├── 📁 database/                     # Data Layer
│   ├── aktienanalyse_de.db         # SQLite Hauptdatenbank
│   ├── schemas/                    # Database Schemas
│   │   ├── __init__.py
│   │   ├── wachstumsprognosen.sql
│   │   ├── live_monitoring.sql
│   │   └── portfolio.sql
│   ├── migrations/                 # Database Migrations
│   └── seeders/                    # Test Data
├── 📁 tests/                       # Test Suite
│   ├── __init__.py
│   ├── test_api/                   # API Tests
│   ├── test_services/              # Service Tests
│   ├── test_frontend/              # Frontend Tests
│   └── integration/                # Integration Tests
├── 📁 docs/                        # Documentation
│   ├── ARCHITECTURE.md             # Diese Datei
│   ├── API.md                      # API Dokumentation
│   ├── DEPLOYMENT.md               # Deployment Guide
│   └── DEVELOPMENT.md              # Development Guide
├── 📁 scripts/                     # Utility Scripts
│   ├── setup.py                   # Setup Script
│   ├── migrate.py                 # Database Migration
│   └── seed_data.py               # Data Seeding
└── 📁 config/                      # Configuration
    ├── development.py
    ├── production.py
    └── testing.py
```

## 🔄 Data Flow Architecture

### Wachstumsprognose Flow

```mermaid
flowchart TD
    START[User Request] --> CACHE{Cache Check}
    CACHE -->|Hit| RETURN[Return Cached Data]
    CACHE -->|Miss| FETCH[Fetch Stock Data]
    FETCH --> CALC[Calculate 5-Factor Score]
    CALC --> RANK[Rank Top 10]
    RANK --> STORE[Store in Database]
    STORE --> CACHE_SET[Update Cache]
    CACHE_SET --> RETURN
    RETURN --> END[Display to User]
```

### Live-Monitoring Flow

```mermaid
flowchart TD
    USER[User Adds Position] --> MODAL[Position Modal]
    MODAL --> VALIDATE[Validate Input]
    VALIDATE --> API[API Call]
    API --> PRICE[Get Current Price]
    PRICE --> CALC[Calculate Values]
    CALC --> STORE[Store Position]
    STORE --> UPDATE[Update Dashboard]
    UPDATE --> NOTIFY[User Notification]
    
    subgraph "Background Process"
        TIMER[60s Timer] --> REFRESH[Refresh Prices]
        REFRESH --> UPDATE_DB[Update Database]
        UPDATE_DB --> PUSH[Push to Frontend]
    end
```

## 💾 Database Design

### Entity Relationship Diagram

```mermaid
erDiagram
    WACHSTUMSPROGNOSEN {
        int id PK
        string symbol
        float wachstums_score
        float prognostizierter_preis
        float erwartete_rendite
        string vertrauen_level
        string risiko_level
        datetime erstellt_am
    }
    
    LIVE_MONITORING_POSITIONS {
        int id PK
        string symbol
        int shares
        float investment_amount
        float entry_price
        float current_price
        float total_value
        float profit_loss
        float profit_loss_percent
        datetime added_at
        datetime last_updated
    }
    
    HISTORICAL_STOCK_DATA {
        int id PK
        string symbol
        float price
        float volume
        datetime timestamp
    }
    
    PORTFOLIO_SIMULATIONS {
        int id PK
        float startkapital
        json allocation
        float expected_return
        datetime created_at
    }
    
    WACHSTUMSPROGNOSEN ||--o{ LIVE_MONITORING_POSITIONS : "symbol"
    LIVE_MONITORING_POSITIONS ||--o{ HISTORICAL_STOCK_DATA : "symbol"
```

### Database Schema Evolution

```sql
-- Version 1: Basic Schema
CREATE TABLE wachstumsprognosen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    wachstums_score REAL NOT NULL,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Version 2: Enhanced Live Monitoring  
CREATE TABLE live_monitoring_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    shares INTEGER NOT NULL,
    investment_amount REAL NOT NULL,
    entry_price REAL,
    current_price REAL,
    total_value REAL,
    profit_loss REAL,
    profit_loss_percent REAL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Version 3: Portfolio Management (Geplant)
CREATE TABLE portfolio_allocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER,
    symbol TEXT NOT NULL,
    target_weight REAL NOT NULL,
    current_weight REAL,
    rebalance_threshold REAL DEFAULT 0.05
);
```

## 🚀 API Architecture

### REST API Design

```yaml
# OpenAPI 3.0 Schema
openapi: 3.0.0
info:
  title: DA-KI API
  version: 2.0.0
  description: Deutsche Aktienanalyse mit KI-Wachstumsprognose

paths:
  /api/wachstumsprognose/top10:
    get:
      summary: Top 10 Wachstumsaktien
      responses:
        200:
          description: Erfolgreiche Antwort
          content:
            application/json:
              schema:
                type: object
                properties:
                  top_10_wachstums_aktien:
                    type: array
                    items:
                      $ref: '#/components/schemas/WachstumsAktie'
                  cache_status:
                    type: string
                  nächste_aktualisierung:
                    type: string

  /api/live-monitoring/add:
    post:
      summary: Position hinzufügen
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PositionRequest'
      responses:
        201:
          description: Position erfolgreich hinzugefügt
          
components:
  schemas:
    WachstumsAktie:
      type: object
      properties:
        symbol:
          type: string
        name:
          type: string
        wachstums_score:
          type: number
        current_price:
          type: number
        prognose_30_tage:
          $ref: '#/components/schemas/Prognose'
          
    PositionRequest:
      type: object
      required:
        - symbol
        - shares
        - investment
      properties:
        symbol:
          type: string
        shares:
          type: integer
          minimum: 1
        investment:
          type: number
          minimum: 0.01
```

### API Versioning Strategy

```python
# Version 1: /api/v1/...  (Legacy)
# Version 2: /api/...     (Current)
# Version 3: /api/v3/...  (Future)

@app.get("/api/v1/wachstumsprognose")  # Deprecated
@app.get("/api/wachstumsprognose/top10")  # Current
@app.get("/api/v3/growth/predictions")  # Future
```

## ⚡ Performance Architecture

### Caching Strategy

```mermaid
graph TB
    REQUEST[API Request] --> L1{L1 Cache<br/>Memory}
    L1 -->|Hit| RETURN[Return Data]
    L1 -->|Miss| L2{L2 Cache<br/>Redis}
    L2 -->|Hit| STORE_L1[Store in L1]
    L2 -->|Miss| DB[(Database)]
    STORE_L1 --> RETURN
    DB --> STORE_L2[Store in L2]
    STORE_L2 --> STORE_L1
```

### Asynchronous Processing

```python
# AsyncIO Pattern für Parallel Processing
async def berechne_alle_aktien_parallel():
    tasks = []
    for symbol in aktien_liste:
        task = asyncio.create_task(berechne_einzelne_aktie(symbol))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

# WebSocket für Real-time Updates  
@app.websocket("/ws/live-monitoring")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        # Send real-time updates
        data = await get_live_monitoring_data()
        await websocket.send_json(data)
        await asyncio.sleep(60)  # 60 second intervals
```

## 🔐 Security Architecture

### Authentication & Authorization

```mermaid
graph TB
    USER[User] --> AUTH[Authentication]
    AUTH --> JWT[JWT Token]
    JWT --> API[API Access]
    API --> RBAC[Role-Based Access]
    RBAC --> RESOURCE[Protected Resource]
```

### Security Measures

```python
# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://10.1.1.110:8054"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting
@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    # Implement rate limiting logic
    pass

# Input Validation
class PositionRequest(BaseModel):
    symbol: str = Field(..., regex="^[A-Z]{1,5}$")
    shares: int = Field(..., gt=0, le=10000)
    investment: float = Field(..., gt=0.01, le=1000000)
```

## 📊 Monitoring & Observability

### Application Metrics

```python
# Prometheus Metrics Integration
from prometheus_client import Counter, Histogram, Gauge

api_requests_total = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint'])
response_time_seconds = Histogram('response_time_seconds', 'Response time in seconds')
active_positions_gauge = Gauge('active_positions', 'Number of active monitoring positions')
```

### Logging Strategy

```python
import logging
import structlog

# Structured Logging
logger = structlog.get_logger()

@app.middleware("http")
async def logging_middleware(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        "api_request",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time
    )
    return response
```

## 🔮 Future Architecture Considerations

### Microservices Evolution

```mermaid
graph TB
    subgraph "Current Monolith"
        MONO[DA-KI Application]
    end
    
    subgraph "Future Microservices"
        AUTH_SVC[🔐 Auth Service]
        GROWTH_SVC[🤖 Growth Service]
        MONITOR_SVC[📊 Monitoring Service]
        PORTFOLIO_SVC[💰 Portfolio Service]
        NOTIFICATION_SVC[📨 Notification Service]
    end
    
    MONO -.-> AUTH_SVC
    MONO -.-> GROWTH_SVC
    MONO -.-> MONITOR_SVC
    MONO -.-> PORTFOLIO_SVC
    MONO -.-> NOTIFICATION_SVC
```

### Cloud-Native Deployment

```yaml
# Kubernetes Deployment Example
apiVersion: apps/v1
kind: Deployment
metadata:
  name: da-ki-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: da-ki-api
  template:
    metadata:
      labels:
        app: da-ki-api
    spec:
      containers:
      - name: api
        image: da-ki/api:latest
        ports:
        - containerPort: 8003
        env:
        - name: DATABASE_URL
          value: "postgresql://..."
        - name: REDIS_URL
          value: "redis://..."
```

### Event-Driven Architecture

```mermaid
graph TB
    EVENT_BUS[Event Bus<br/>Apache Kafka]
    
    GROWTH_SVC[Growth Service] --> EVENT_BUS
    EVENT_BUS --> MONITOR_SVC[Monitoring Service]
    EVENT_BUS --> PORTFOLIO_SVC[Portfolio Service]
    EVENT_BUS --> NOTIFICATION_SVC[Notification Service]
    
    EVENT_BUS --> ANALYTICS[Analytics Pipeline]
    EVENT_BUS --> AUDIT[Audit Logging]
```

## 📋 Architecture Decision Records (ADRs)

### ADR-001: Teilprojekt-basierte Architektur
- **Status**: Accepted
- **Context**: Modulare Entwicklung und klare Verantwortlichkeiten
- **Decision**: 5-Teilprojekt Struktur (CORE, FRONTEND, KI, LIVE, DEPO)
- **Consequences**: Bessere Skalierbarkeit, einfachere Wartung

### ADR-002: SQLite als primäre Datenbank
- **Status**: Accepted  
- **Context**: Einfache Deployment, ausreichende Performance für MVP
- **Decision**: SQLite für lokale Entwicklung, Migration zu PostgreSQL geplant
- **Consequences**: Schnelle Entwicklung, spätere Migration erforderlich

### ADR-003: FastAPI + Dash Framework
- **Status**: Accepted
- **Context**: Moderne Python Web-Frameworks
- **Decision**: FastAPI für API, Dash für interaktive Dashboards
- **Consequences**: Hohe Entwicklungsgeschwindigkeit, Python-Konsistenz

---

**📝 Architektur-Dokumentation | Version 2.0 | DA-KI Project**

*Entwickelt mit [Claude Code](https://claude.ai/code) - Moderne KI-gestützte Softwareentwicklung*