# DA-KI - Automated Stock Portfolio Management System

[![CI/CD Pipeline](https://github.com/your-org/da-ki/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/your-org/da-ki/actions)
[![Code Coverage](https://codecov.io/gh/your-org/da-ki/branch/main/graph/badge.svg)](https://codecov.io/gh/your-org/da-ki)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=your-org_da-ki&metric=security_rating)](https://sonarcloud.io/dashboard?id=your-org_da-ki)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://python.org)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🚀 Overview

DA-KI is an advanced automated stock portfolio management system that combines AI-powered analysis with secure trading capabilities. The system provides intelligent stock recommendations, portfolio optimization, and automated trading through broker APIs.

## ✨ Key Features

### 🎯 Core Functionality
- **AI-Powered Analysis**: Technical indicators, sentiment analysis, and ML predictions
- **Portfolio Management**: Multi-user portfolio tracking with real-time valuations
- **Automated Trading**: Integration with broker APIs for automated buy/sell operations
- **Risk Management**: Advanced risk assessment and position sizing

### 🛡️ Security & Reliability
- **Enterprise Security**: JWT authentication, encrypted API keys, secure password hashing
- **Input Validation**: Comprehensive data validation with Pydantic models
- **Error Handling**: Robust error handling with detailed logging
- **Health Monitoring**: System health checks and performance metrics

### 🏗️ Architecture
- **Microservices Design**: Clean separation of concerns with service layers
- **Plugin Architecture**: Extensible data source plugins
- **API-First**: RESTful API with OpenAPI documentation
- **Scalable**: Built for horizontal scaling and high availability

## 📋 Recent Code Quality Improvements

### ✅ Security Enhancements
- ✅ **Fixed Password Security**: Always hash passwords, even in development
- ✅ **Secure Configuration**: Environment-based secrets management
- ✅ **Input Validation**: Comprehensive Pydantic model validation
- ✅ **JWT Security**: Proper token handling and validation

### ✅ Architecture Improvements
- ✅ **Service Layer**: Clean separation between API and business logic
- ✅ **Dependency Injection**: Proper dependency management
- ✅ **Error Handling**: Consistent error responses and logging
- ✅ **Database Abstraction**: Improved database access layer

### ✅ Development Infrastructure
- ✅ **Poetry Integration**: Modern Python dependency management
- ✅ **Code Quality Tools**: Black, Ruff, MyPy, and Bandit
- ✅ **Pre-commit Hooks**: Automated code quality checks
- ✅ **CI/CD Pipeline**: GitHub Actions with comprehensive testing
- ✅ **Test Framework**: pytest with coverage reporting

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, FastAPI, SQLite/PostgreSQL
- **ML/AI**: XGBoost, LightGBM, scikit-learn, pandas
- **Authentication**: JWT with bcrypt password hashing
- **Testing**: pytest, pytest-asyncio, httpx
- **Code Quality**: Black, Ruff, MyPy, Bandit
- **CI/CD**: GitHub Actions, Poetry
- **Documentation**: OpenAPI/Swagger, automatic API docs

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Poetry (for dependency management)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/da-ki.git
   cd da-ki
   ```

2. **Install dependencies**
   ```bash
   # Install Poetry if not already installed
   curl -sSL https://install.python-poetry.org | python3 -

   # Install project dependencies
   poetry install
   ```

3. **Set up environment**
   ```bash
   # Copy example environment file
   cp config/dev_secrets.json.example config/dev_secrets.json
   
   # Edit configuration file with your settings
   nano config/dev_secrets.json
   ```

4. **Initialize database**
   ```bash
   poetry run python -m src.database.db_setup
   ```

5. **Run the development server**
   ```bash
   # Set environment
   export DAKI_ENV=development
   
   # Start server
   poetry run uvicorn src.main_improved:app --reload --host 127.0.0.1 --port 8000
   ```

6. **Access the API**
   - API Documentation: http://localhost:8000/api/docs
   - Health Check: http://localhost:8000/health/liveness
   - System Status: http://localhost:8000/api/system/status

## 🧪 Development

### Code Quality

```bash
# Format code
poetry run black .
poetry run isort .

# Lint code
poetry run ruff check .
poetry run mypy src/

# Security scan
poetry run bandit -r src/

# Run all quality checks
poetry run pre-commit run --all-files
```

### Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test categories
poetry run pytest -m unit
poetry run pytest -m integration
poetry run pytest -m "not slow"
```

### Database Management

```bash
# Initialize database
poetry run python -m src.database.db_setup

# Reset database (development only)
poetry run python -m src.database.db_setup --reset

# Check database status
poetry run python -c "from src.database.db_access_extended import DBAccessExtended; import asyncio; print(asyncio.run(DBAccessExtended().check_connection()))"
```

## 📚 API Documentation

### Authentication

```bash
# Register new user
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "password": "securepassword123"}'

# Login
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=newuser&password=securepassword123"
```

### Portfolio Management

```bash
# Add stock to portfolio
curl -X POST "http://localhost:8000/api/portfolio/stocks" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "quantity": 10, "average_buy_price": 150.0}'

# Get portfolio
curl -X GET "http://localhost:8000/api/portfolio/stocks" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Stock Analysis

```bash
# Start analysis
curl -X POST "http://localhost:8000/api/analysis/start" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tickers": ["AAPL", "GOOGL", "MSFT"]}'
```

## 🔧 Configuration

### Environment Variables

```bash
# Required for production
export DAKI_ENV=production
export DAKI_SECRET_KEY=your-super-secret-jwt-key
export DAKI_DATABASE_URL=postgresql://user:pass@localhost/daki
export DAKI_MASTER_ENCRYPTION_KEY=base64-encoded-encryption-key

# Optional API keys
export DAKI_ALPHA_VANTAGE_KEY=your-alpha-vantage-key
export DAKI_YAHOO_FINANCE_KEY=your-yahoo-finance-key
export DAKI_BROKER_API_KEY=your-broker-api-key
export DAKI_BROKER_API_SECRET=your-broker-api-secret
```

### Development Configuration

Create `config/dev_secrets.json`:

```json
{
  "database": {
    "url": "sqlite:///./data/daki.db"
  },
  "jwt": {
    "secret_key": "your-development-jwt-secret",
    "access_token_expire_minutes": 30,
    "refresh_token_expire_days": 7
  },
  "api_keys": {
    "alpha_vantage": "your-dev-api-key",
    "yahoo_finance": "your-dev-api-key"
  },
  "users": {
    "admin": {
      "username": "admin",
      "password": "admin-dev-password"
    }
  }
}
```

## 🚀 Deployment

### Docker Deployment

```bash
# Build image
docker build -t da-ki:latest .

# Run container
docker run -d \
  --name da-ki \
  -p 8000:8000 \
  -e DAKI_ENV=production \
  -e DAKI_SECRET_KEY=your-secret-key \
  -v /path/to/data:/app/data \
  da-ki:latest
```

### LXC Container Deployment

```bash
# Create LXC container
lxc launch ubuntu:22.04 da-ki-container

# Execute setup script
lxc exec da-ki-container -- bash /path/to/setup-script.sh

# Configure reverse proxy (nginx)
# See docs/deployment/ for detailed instructions
```

## 📈 Monitoring

### Health Checks

- **Liveness**: `GET /health/liveness` - Basic application health
- **Readiness**: `GET /health/readiness` - Application ready to serve traffic
- **System Status**: `GET /api/system/status` - Detailed system information

### Metrics

- Database connection status
- Active user sessions
- Portfolio valuations
- Analysis performance
- API response times

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run quality checks (`poetry run pre-commit run --all-files`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Standards

- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Maintain test coverage above 90%
- Use semantic commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- **Documentation**: [Full documentation](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/da-ki/issues)
- **Security**: Report security issues to security@your-org.com

## 🗺️ Roadmap

### Phase 1: Foundation (Completed ✅)
- ✅ Basic API framework
- ✅ User authentication
- ✅ Portfolio management
- ✅ Code quality improvements

### Phase 2: Analysis Engine (In Progress 🚧)
- 🚧 Complete technical indicators
- 🚧 Event-driven analysis
- 🚧 ML prediction models
- 🚧 Plugin system

### Phase 3: Trading Integration (Planned 📋)
- 📋 Broker API integration
- 📋 Automated trading rules
- 📋 Risk management
- 📋 Performance tracking

### Phase 4: Advanced Features (Future 🔮)
- 🔮 Advanced ML models
- 🔮 Social sentiment analysis
- 🔮 Portfolio optimization
- 🔮 Mobile application

---

**Built with ❤️ by the DA-KI team**