# ⚙️ DA-KI Technisches Konzept & Implementation Strategy

## 📋 Technologie-Übersicht

**DA-KI** implementiert eine moderne, skalierbare Fintech-Architektur basierend auf Python-Technologien mit KI-Integration für Real-time Aktienanalyse.

### 🎯 Technische Mission
"Hochperformante, skalierbare KI-Plattform für Real-time Finanzmarktanalyse mit Enterprise-Grade Zuverlässigkeit."

---

## 🏗️ System Architecture Deep Dive

### 🔧 Technology Stack

#### Core Technologies
```yaml
Backend Framework:     FastAPI 0.115+ (Async-First)
Frontend Framework:    Plotly Dash 2.18+ (Reactive Components)
Database:             SQLite → PostgreSQL (Production)
Caching:              Redis 7+ (Multi-Level)
Message Queue:        Celery + Redis
Real-time:            WebSockets (Socket.IO)
```

#### Data Processing Stack
```yaml
Data Analysis:        Pandas 2.2+, NumPy 1.26+
Machine Learning:     Scikit-learn 1.5+, XGBoost
Time Series:          Prophet, ARIMA Models
Market Data:          Yahoo Finance API, Alpha Vantage
Sentiment Analysis:   NLTK, TextBlob, VADER
```

#### Infrastructure Stack
```yaml
Containerization:     Docker + Docker Compose
Orchestration:        Kubernetes (Production)
Cloud Provider:       AWS (Primary), Azure (Backup)
Monitoring:           Prometheus + Grafana
Logging:              ELK Stack (Elasticsearch, Logstash, Kibana)
CI/CD:                GitHub Actions + ArgoCD
```

### 🧠 KI-Algorithmus Architektur

#### 5-Faktor Scoring System

```python
# Scoring Formula (Vereinfacht)
def calculate_growth_score(stock_data):
    factors = {
        'performance_score': weight_performance * performance_factor(stock_data),
        'fundamental_score': weight_fundamental * fundamental_factor(stock_data),
        'sentiment_score': weight_sentiment * sentiment_factor(stock_data),
        'sector_score': weight_sector * sector_factor(stock_data),
        'momentum_score': weight_momentum * momentum_factor(stock_data)
    }
    
    # Gewichtete Summe mit Normalisierung
    final_score = normalize_score(sum(factors.values()))
    return min(max(final_score, 0), 100)  # 0-100 Skala
```

#### Faktor-Details

| Faktor | Gewichtung | Datenquellen | Update-Frequenz |
|--------|------------|--------------|-----------------|
| **Performance** | 30% | Historische Kursdaten, Volatilität | Real-time |
| **Fundamental** | 25% | P/E, P/B, Debt/Equity, ROE | Täglich |
| **Sentiment** | 20% | News-Analyse, Social Media | 4x täglich |
| **Sektor** | 15% | Sektor-Performance, Korrelationen | Täglich |
| **Momentum** | 10% | RSI, MACD, Moving Averages | Real-time |

### 📊 Data Pipeline Architecture

```mermaid
graph TB
    subgraph "Data Sources"
        YF[Yahoo Finance API]
        AV[Alpha Vantage API]
        NEWS[News APIs]
        SOCIAL[Social Media APIs]
    end
    
    subgraph "Data Ingestion Layer"
        COLLECTOR[Data Collector Service]
        VALIDATOR[Data Validation Service]
        NORMALIZER[Data Normalization Service]
    end
    
    subgraph "Processing Layer"
        CALCULATOR[Score Calculator Engine]
        ML[ML Prediction Models]
        SENTIMENT[Sentiment Analysis]
        RISK[Risk Assessment]
    end
    
    subgraph "Storage Layer"
        CACHE[(Redis Cache)]
        DB[(PostgreSQL)]
        TIMESERIES[(InfluxDB)]
    end
    
    subgraph "API Layer"
        FASTAPI[FastAPI Backend]
        WEBSOCKET[WebSocket Handler]
        SCHEDULER[Background Tasks]
    end
    
    subgraph "Frontend Layer"
        DASH[Dash Dashboard]
        MOBILE[Mobile App - Future]
    end
    
    YF --> COLLECTOR
    AV --> COLLECTOR
    NEWS --> COLLECTOR
    SOCIAL --> COLLECTOR
    
    COLLECTOR --> VALIDATOR
    VALIDATOR --> NORMALIZER
    NORMALIZER --> CALCULATOR
    NORMALIZER --> ML
    NORMALIZER --> SENTIMENT
    
    CALCULATOR --> CACHE
    ML --> CACHE
    SENTIMENT --> CACHE
    CALCULATOR --> DB
    ML --> TIMESERIES
    
    CACHE --> FASTAPI
    DB --> FASTAPI
    TIMESERIES --> FASTAPI
    
    FASTAPI --> WEBSOCKET
    FASTAPI --> SCHEDULER
    
    FASTAPI --> DASH
    WEBSOCKET --> DASH
```

---

## 🚀 Performance & Scalability Konzept

### 📈 Skalierungs-Strategie

#### Horizontale Skalierung
```yaml
API Services:
  - Load Balancer: NGINX + HAProxy
  - Auto-Scaling: Kubernetes HPA
  - Service Mesh: Istio (Future)
  
Data Processing:
  - Distributed Computing: Celery Workers
  - Message Queue: Redis Cluster
  - Database Sharding: By Stock Symbol
  
Caching Strategy:
  - L1: Application Memory (5 min TTL)
  - L2: Redis Cache (1 hour TTL)  
  - L3: Database (Persistent)
```

#### Performance Targets

| Service | Response Time | Throughput | Availability |
|---------|---------------|------------|--------------|
| **API Endpoints** | <200ms | 1000 RPS | 99.9% |
| **WebSocket Updates** | <50ms | 10k concurrent | 99.5% |
| **Score Calculation** | <5s (467 stocks) | 1 update/min | 99.9% |
| **Database Queries** | <100ms | 500 QPS | 99.95% |

### ⚡ Caching Architecture

#### Multi-Level Caching Strategy
```python
# Caching Implementation Pattern
class CacheManager:
    def __init__(self):
        self.l1_cache = TTLCache(maxsize=1000, ttl=300)  # 5 min
        self.l2_cache = RedisCache(ttl=3600)             # 1 hour
        self.l3_cache = DatabaseCache()                   # Persistent
    
    async def get_stock_data(self, symbol: str):
        # L1 Cache Check
        if data := self.l1_cache.get(symbol):
            return data
        
        # L2 Cache Check
        if data := await self.l2_cache.get(symbol):
            self.l1_cache[symbol] = data
            return data
        
        # L3 Database Fallback
        data = await self.l3_cache.get(symbol)
        await self.l2_cache.set(symbol, data)
        self.l1_cache[symbol] = data
        return data
```

---

## 🔄 Real-time Data Processing

### 📡 WebSocket Implementation

#### Real-time Update Flow
```python
# WebSocket Manager für Live Updates
class LiveUpdateManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.update_scheduler = AsyncIOScheduler()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast_update(self, data: dict):
        if self.active_connections:
            tasks = [
                self.send_to_client(conn, data) 
                for conn in self.active_connections
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def send_to_client(self, websocket: WebSocket, data: dict):
        try:
            await websocket.send_json(data)
        except ConnectionClosedError:
            await self.disconnect(websocket)
```

#### Update-Frequenzen
- **Kursdaten**: Jede Minute während Handelszeiten
- **Scoring**: Alle 5 Minuten
- **Portfolio-Werte**: Real-time bei Kursänderungen
- **News/Sentiment**: Alle 15 Minuten

### 🔄 Background Task Processing

#### Celery Task Architecture
```python
# Background Tasks mit Celery
@celery.task(bind=True, max_retries=3)
def update_stock_scores(self, stock_symbols: List[str]):
    try:
        for symbol in stock_symbols:
            # Hole aktuelle Daten
            market_data = fetch_market_data(symbol)
            
            # Berechne Score
            score = calculate_growth_score(market_data)
            
            # Speichere in DB + Cache
            save_score_to_database(symbol, score)
            update_cache(symbol, score)
            
            # Sende WebSocket Update
            broadcast_score_update(symbol, score)
            
    except Exception as exc:
        self.retry(countdown=60, exc=exc)

# Scheduler für regelmäßige Updates
@celery.beat_schedule
def schedule_score_updates():
    return {
        'update-scores-every-5-minutes': {
            'task': 'update_stock_scores',
            'schedule': crontab(minute='*/5'),
            'args': (get_all_stock_symbols(),)
        }
    }
```

---

## 🔐 Security & Compliance

### 🛡️ Security Architecture

#### Authentication & Authorization
```python
# JWT-basierte Authentifizierung
class SecurityManager:
    def __init__(self):
        self.jwt_secret = os.getenv("JWT_SECRET_KEY")
        self.algorithm = "HS256"
        self.token_expiry = timedelta(hours=24)
    
    def create_access_token(self, user_data: dict) -> str:
        payload = {
            "user_id": user_data["id"],
            "email": user_data["email"],
            "exp": datetime.utcnow() + self.token_expiry,
            "iat": datetime.utcnow(),
            "scope": user_data.get("scope", "read")
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
```

#### Data Protection (DSGVO-Konform)
- **Datenverschlüsselung**: AES-256 für sensitive Daten
- **PII-Anonymisierung**: Keine Speicherung von Personendaten ohne Consent
- **Right to be Forgotten**: Automated Data Deletion APIs
- **Audit Logging**: Vollständige Nachverfolgung aller Datenzugriffe

#### API Security
```python
# Rate Limiting & Security Headers
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

@app.get("/api/stocks")
@limiter.limit("100/minute")
async def get_stocks(request: Request):
    return stock_data
```

---

## 📊 Database Design & Data Models

### 🗄️ Database Schema Evolution

#### Current Schema (SQLite) → Target (PostgreSQL)
```sql
-- Erweiterte Wachstumsprognosen Tabelle
CREATE TABLE wachstumsprognosen (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    wachstums_score DECIMAL(5,2) NOT NULL,
    
    -- 5-Faktor Aufschlüsselung
    performance_score DECIMAL(5,2),
    fundamental_score DECIMAL(5,2),
    sentiment_score DECIMAL(5,2),
    sector_score DECIMAL(5,2),
    momentum_score DECIMAL(5,2),
    
    -- Prognose-Daten
    prognostizierter_preis DECIMAL(10,2),
    erwartete_rendite DECIMAL(5,2),
    vertrauen_level VARCHAR(20),
    risiko_level VARCHAR(20),
    
    -- Metadaten
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    gueltig_bis TIMESTAMP,
    model_version VARCHAR(10),
    
    INDEX idx_symbol_datum (symbol, erstellt_am),
    INDEX idx_score (wachstums_score DESC)
);

-- Erweiterte Live Monitoring Tabelle
CREATE TABLE live_monitoring_positions (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    symbol VARCHAR(10) NOT NULL,
    
    -- Position Details
    shares INTEGER NOT NULL,
    investment_amount DECIMAL(12,2) NOT NULL,
    entry_price DECIMAL(10,2),
    current_price DECIMAL(10,2),
    
    -- Berechnete Werte
    total_value DECIMAL(12,2),
    profit_loss DECIMAL(12,2),
    profit_loss_percent DECIMAL(5,2),
    
    -- Alerts & Limits
    stop_loss DECIMAL(10,2),
    take_profit DECIMAL(10,2),
    alert_enabled BOOLEAN DEFAULT false,
    
    -- Metadaten
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    
    INDEX idx_user_symbol (user_id, symbol),
    INDEX idx_status_updated (status, last_updated)
);

-- Historische Kursdaten (Partitioniert)
CREATE TABLE historical_stock_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    
    -- OHLCV Daten
    open_price DECIMAL(10,2),
    high_price DECIMAL(10,2),
    low_price DECIMAL(10,2),
    close_price DECIMAL(10,2),
    volume BIGINT,
    
    -- Technische Indikatoren
    rsi DECIMAL(5,2),
    macd DECIMAL(8,4),
    moving_avg_20 DECIMAL(10,2),
    moving_avg_50 DECIMAL(10,2),
    
    -- Partitionierung nach Jahr
    PRIMARY KEY (id, date),
    INDEX idx_symbol_date (symbol, date)
) PARTITION BY RANGE (YEAR(date));
```

#### Time-Series Data (InfluxDB)
```sql
-- Real-time Metriken für Performance Monitoring
CREATE MEASUREMENT stock_metrics (
    time TIMESTAMP,
    symbol TAG,
    
    -- Preis-Metriken
    price FLOAT,
    volume FLOAT,
    change_percent FLOAT,
    
    -- System-Metriken
    calculation_time FLOAT,
    data_freshness INTEGER,
    api_response_time FLOAT
);

-- User Activity Tracking
CREATE MEASUREMENT user_activity (
    time TIMESTAMP,
    user_id TAG,
    action TAG,
    
    -- Activity Details
    duration FLOAT,
    success BOOLEAN,
    error_code INTEGER
);
```

---

## 🤖 Machine Learning Pipeline

### 📈 Predictive Models

#### Model Architecture
```python
# Ensemble Model für Preis-Prognosen
class StockPredictionEnsemble:
    def __init__(self):
        self.models = {
            'xgboost': XGBRegressor(n_estimators=100),
            'random_forest': RandomForestRegressor(n_estimators=50),
            'lstm': LSTMPredictor(),
            'arima': ARIMAPredictor()
        }
        self.meta_model = LinearRegression()
    
    def train(self, X_train, y_train):
        # Level 1: Basis-Modelle trainieren
        predictions = {}
        for name, model in self.models.items():
            model.fit(X_train, y_train)
            predictions[name] = model.predict(X_train)
        
        # Level 2: Meta-Model für Ensemble
        X_meta = np.column_stack(list(predictions.values()))
        self.meta_model.fit(X_meta, y_train)
    
    def predict(self, X_test):
        # Vorhersagen aller Basis-Modelle
        base_predictions = []
        for model in self.models.values():
            pred = model.predict(X_test)
            base_predictions.append(pred)
        
        # Meta-Model kombiniert Vorhersagen
        X_meta = np.column_stack(base_predictions)
        final_prediction = self.meta_model.predict(X_meta)
        
        return final_prediction
```

#### Feature Engineering Pipeline
```python
# Feature Engineering für Aktienanalyse
class FeatureEngineer:
    def create_features(self, stock_data: pd.DataFrame) -> pd.DataFrame:
        df = stock_data.copy()
        
        # Technische Indikatoren
        df['rsi'] = calculate_rsi(df['close'])
        df['macd'] = calculate_macd(df['close'])
        df['bollinger_upper'], df['bollinger_lower'] = calculate_bollinger_bands(df['close'])
        
        # Price Features
        df['price_change_1d'] = df['close'].pct_change(1)
        df['price_change_7d'] = df['close'].pct_change(7)
        df['volatility_20d'] = df['close'].rolling(20).std()
        
        # Volume Features
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
        df['price_volume_trend'] = (df['close'] - df['close'].shift(1)) * df['volume']
        
        # Fundamental Features (wenn verfügbar)
        df['pe_ratio'] = df['market_cap'] / df['earnings']
        df['pb_ratio'] = df['market_cap'] / df['book_value']
        
        # Sentiment Features
        df['news_sentiment'] = self.get_sentiment_score(df.index)
        df['social_sentiment'] = self.get_social_media_sentiment(df.index)
        
        return df.dropna()
```

### 🧪 Model Training & Validation

#### Cross-Validation Strategy
```python
# Time Series Cross-Validation
class TimeSeriesCrossValidator:
    def __init__(self, n_splits=5, test_size=30):
        self.n_splits = n_splits
        self.test_size = test_size
    
    def split(self, X, y):
        n_samples = len(X)
        test_size = self.test_size
        
        for i in range(self.n_splits):
            # Training set: alles bis zum Test-Zeitraum
            train_end = n_samples - (self.n_splits - i) * test_size
            train_start = max(0, train_end - 252)  # 1 Jahr Training
            
            # Test set: nächste 30 Tage
            test_start = train_end
            test_end = min(n_samples, test_start + test_size)
            
            train_indices = range(train_start, train_end)
            test_indices = range(test_start, test_end)
            
            yield train_indices, test_indices

# Model Performance Monitoring
class ModelPerformanceTracker:
    def track_prediction_accuracy(self, symbol: str, predicted: float, actual: float):
        accuracy = 1 - abs(predicted - actual) / actual
        
        # Speichere in InfluxDB für Monitoring
        self.influx_client.write_points([{
            "measurement": "model_performance",
            "tags": {"symbol": symbol, "model": "ensemble"},
            "fields": {
                "predicted_price": predicted,
                "actual_price": actual,
                "accuracy": accuracy,
                "absolute_error": abs(predicted - actual)
            }
        }])
```

---

## 🚀 Deployment & Operations

### 🐳 Containerization Strategy

#### Docker Setup
```dockerfile
# Multi-Stage Build für Production
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim as production

# Security: Non-root user
RUN groupadd -r da-ki && useradd -r -g da-ki da-ki

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

# Make sure scripts are executable
RUN chmod +x scripts/*.sh

USER da-ki
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "api.api_top10_final:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose für Development
```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8003:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/da_ki
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=development
    depends_on:
      - postgres
      - redis
    volumes:
      - ./api:/app/api
      - ./services:/app/services
  
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "8054:8050"
    environment:
      - API_BASE_URL=http://api:8000
    depends_on:
      - api
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: da_ki
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/migrations:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
  
  celery-worker:
    build:
      context: .
      dockerfile: Dockerfile
    command: celery -A services.tasks worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/da_ki
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
  
  celery-beat:
    build:
      context: .
      dockerfile: Dockerfile
    command: celery -A services.tasks beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/da_ki
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
  redis_data:
```

### ☸️ Kubernetes Production Setup

#### Kubernetes Manifests
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: da-ki-api
  labels:
    app: da-ki-api
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
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: da-ki-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: da-ki-config
              key: redis-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: da-ki-api-service
spec:
  selector:
    app: da-ki-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

### 📊 Monitoring & Observability

#### Prometheus Metrics
```python
# Monitoring Integration
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Business Metrics
api_requests_total = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
stock_calculations_total = Counter('stock_calculations_total', 'Total stock calculations performed')
active_users_gauge = Gauge('active_users', 'Number of currently active users')

# Performance Metrics
request_duration = Histogram('request_duration_seconds', 'Request duration in seconds', ['endpoint'])
score_calculation_duration = Histogram('score_calculation_duration_seconds', 'Score calculation duration')
database_query_duration = Histogram('database_query_duration_seconds', 'Database query duration')

# System Health Metrics
cache_hit_rate = Gauge('cache_hit_rate', 'Cache hit rate percentage')
api_response_time = Gauge('api_response_time_ms', 'Average API response time')
websocket_connections = Gauge('websocket_connections', 'Number of active WebSocket connections')

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    duration = time.time() - start_time
    request_duration.labels(endpoint=request.url.path).observe(duration)
    api_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    return response

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

#### Grafana Dashboard Configuration
```json
{
  "dashboard": {
    "title": "DA-KI System Overview",
    "panels": [
      {
        "title": "API Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(api_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time P95",
        "type": "stat",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(request_duration_seconds_bucket[5m]))",
            "legendFormat": "P95 Response Time"
          }
        ]
      },
      {
        "title": "Active Users",
        "type": "stat",
        "targets": [
          {
            "expr": "active_users_gauge",
            "legendFormat": "Active Users"
          }
        ]
      },
      {
        "title": "Cache Hit Rate",
        "type": "gauge",
        "targets": [
          {
            "expr": "cache_hit_rate",
            "legendFormat": "Cache Hit Rate %"
          }
        ]
      }
    ]
  }
}
```

---

## 🔄 Development Workflow

### 🛠️ Development Environment Setup

#### Local Development
```bash
# Setup Script für Entwickler
#!/bin/bash
# scripts/setup-dev.sh

echo "🚀 Setting up DA-KI Development Environment..."

# Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Pre-commit Hooks
pre-commit install

# Database Setup
python scripts/setup_database.py

# Environment Variables
cp .env.example .env
echo "Please configure .env file with your API keys"

# Start Services
docker-compose -f docker-compose.dev.yml up -d postgres redis

echo "✅ Development environment ready!"
echo "Run: python api/api_top10_final.py"
```

#### Code Quality Tools
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ["--max-line-length=120"]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ["-r", ".", "-x", "tests/"]
```

### 🧪 Testing Strategy

#### Test Pyramid Implementation
```python
# tests/conftest.py - Test Fixtures
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.api_top10_final import app
from services.database import get_db

# Test Database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_stock_data():
    return {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "current_price": 150.0,
        "market_cap": 2500000000000,
        "pe_ratio": 25.5
    }

# Unit Tests
class TestGrowthPredictor:
    def test_calculate_performance_score(self, sample_stock_data):
        predictor = GrowthPredictor()
        score = predictor.calculate_performance_score(sample_stock_data)
        assert 0 <= score <= 100

    def test_score_calculation_edge_cases(self):
        # Test mit extremen Werten
        edge_case_data = {"current_price": 0, "market_cap": -1000}
        predictor = GrowthPredictor()
        score = predictor.calculate_growth_score(edge_case_data)
        assert score >= 0  # Score sollte nie negativ sein

# Integration Tests
class TestAPIIntegration:
    def test_get_wachstumsprognose_endpoint(self, client):
        response = client.get("/api/wachstumsprognose/top10")
        assert response.status_code == 200
        data = response.json()
        assert "top_10_wachstums_aktien" in data
        assert len(data["top_10_wachstums_aktien"]) <= 10

    def test_add_position_endpoint(self, client):
        position_data = {
            "symbol": "AAPL",
            "shares": 10,
            "investment": 1500.0
        }
        response = client.post("/api/live-monitoring/add", json=position_data)
        assert response.status_code == 201
        assert "position_id" in response.json()

# End-to-End Tests
class TestE2EWorkflow:
    def test_complete_user_journey(self, client):
        # 1. Get stock recommendations
        recommendations = client.get("/api/wachstumsprognose/top10")
        assert recommendations.status_code == 200
        
        # 2. Add position to monitoring
        top_stock = recommendations.json()["top_10_wachstums_aktien"][0]
        position = {
            "symbol": top_stock["symbol"],
            "shares": 5,
            "investment": 1000.0
        }
        add_response = client.post("/api/live-monitoring/add", json=position)
        assert add_response.status_code == 201
        
        # 3. Check portfolio summary
        portfolio = client.get("/api/monitoring/summary")
        assert portfolio.status_code == 200
        assert portfolio.json()["total_positions"] >= 1
```

---

## 📈 Migration & Upgrade Path

### 🔄 Database Migration Strategy

#### Alembic Migration Setup
```python
# alembic/versions/001_initial_schema.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create enhanced tables
    op.create_table(
        'wachstumsprognosen_v2',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('symbol', sa.String(10), nullable=False),
        sa.Column('wachstums_score', sa.Numeric(5,2), nullable=False),
        sa.Column('performance_score', sa.Numeric(5,2)),
        sa.Column('fundamental_score', sa.Numeric(5,2)),
        sa.Column('sentiment_score', sa.Numeric(5,2)),
        sa.Column('sector_score', sa.Numeric(5,2)),
        sa.Column('momentum_score', sa.Numeric(5,2)),
        sa.Column('erstellt_am', sa.DateTime, server_default=sa.func.now()),
        sa.Column('model_version', sa.String(10), default='2.0'),
    )
    
    # Migrate existing data
    op.execute("""
        INSERT INTO wachstumsprognosen_v2 (symbol, wachstums_score, erstellt_am)
        SELECT symbol, wachstums_score, erstellt_am 
        FROM wachstumsprognosen
    """)

def downgrade():
    op.drop_table('wachstumsprognosen_v2')
```

#### Zero-Downtime Deployment
```bash
#!/bin/bash
# scripts/deploy.sh - Blue-Green Deployment

echo "🚀 Starting zero-downtime deployment..."

# 1. Deploy new version to blue environment
kubectl apply -f k8s/blue-deployment.yaml

# 2. Wait for readiness
kubectl wait --for=condition=available deployment/da-ki-api-blue --timeout=300s

# 3. Run database migrations
kubectl exec deployment/da-ki-api-blue -- python manage.py migrate

# 4. Run smoke tests
kubectl exec deployment/da-ki-api-blue -- python -m pytest tests/smoke/

# 5. Switch traffic to blue
kubectl patch service da-ki-api-service -p '{"spec":{"selector":{"version":"blue"}}}'

# 6. Wait and verify
sleep 30
curl -f http://da-ki-api-service/health || (echo "Health check failed!" && exit 1)

# 7. Scale down green environment
kubectl scale deployment da-ki-api-green --replicas=0

echo "✅ Deployment completed successfully!"
```

---

**⚙️ Technisches Konzept | Version 1.0 | DA-KI Project**

*Entwickelt mit [Claude Code](https://claude.ai/code) - Moderne KI-gestützte Softwarearchitektur*