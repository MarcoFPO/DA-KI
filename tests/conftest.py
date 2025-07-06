"""
Test configuration and fixtures.
"""
import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set test environment
os.environ["DAKI_ENV"] = "test"

from src.main_improved import app
from src.database.db_access_extended import DBAccessExtended
from src.config.config_improved import SecureConfig


@pytest.fixture(scope="session")
def test_database():
    """Create a temporary test database."""
    # Create temporary database file
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db.close()
    
    # Override database configuration for tests
    os.environ["DAKI_DATABASE_URL"] = f"sqlite:///{temp_db.name}"
    
    yield temp_db.name
    
    # Cleanup
    os.unlink(temp_db.name)


@pytest.fixture
def db_access(test_database):
    """Get database access instance for testing."""
    db = DBAccessExtended()
    # Initialize database schema if needed
    # TODO: Add database schema creation
    return db


@pytest.fixture
def client():
    """Get FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def test_user_data():
    """Test user data."""
    return {
        "username": "testuser",
        "password": "testpassword123"
    }


@pytest.fixture
def test_stock_data():
    """Test stock data."""
    return {
        "ticker": "AAPL",
        "quantity": 10.0,
        "average_buy_price": 150.0
    }


@pytest.fixture
def auth_headers(client, test_user_data):
    """Get authentication headers for test user."""
    # Register test user
    client.post("/api/auth/register", json=test_user_data)
    
    # Login and get token
    response = client.post(
        "/api/auth/token",
        data={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
    )
    
    token_data = response.json()
    return {"Authorization": f"Bearer {token_data['access_token']}"}


@pytest.fixture(autouse=True)
def reset_config():
    """Reset configuration before each test."""
    SecureConfig._is_loaded = False
    SecureConfig._secrets = {}
    yield
    SecureConfig._is_loaded = False
    SecureConfig._secrets = {}