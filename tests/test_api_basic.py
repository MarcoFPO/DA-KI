"""
Basic API tests to verify improved functionality.
"""
import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_liveness(client: TestClient):
    """Test liveness health check."""
    response = client.get("/health/liveness")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


def test_health_readiness(client: TestClient):
    """Test readiness health check."""
    response = client.get("/health/readiness")
    # May fail if database is not properly initialized
    assert response.status_code in [200, 503]


def test_user_registration(client: TestClient):
    """Test user registration with validation."""
    # Valid registration
    user_data = {
        "username": "testuser123",
        "password": "securepassword123"
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User registered successfully"
    assert "data" in data
    assert data["data"]["username"] == user_data["username"]


def test_user_registration_validation(client: TestClient):
    """Test user registration validation."""
    # Invalid username (too short)
    response = client.post("/api/auth/register", json={
        "username": "ab",
        "password": "password123"
    })
    assert response.status_code == 422
    
    # Invalid password (too short)
    response = client.post("/api/auth/register", json={
        "username": "validuser",
        "password": "short"
    })
    assert response.status_code == 422


def test_authentication_flow(client: TestClient):
    """Test complete authentication flow."""
    # Register user
    user_data = {
        "username": "authtest",
        "password": "authpassword123"
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    
    # Login
    response = client.post("/api/auth/token", data={
        "username": user_data["username"],
        "password": user_data["password"]
    })
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"
    
    # Access protected endpoint
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    user_info = response.json()
    assert user_info["username"] == user_data["username"]


def test_stock_validation(client: TestClient, auth_headers: dict):
    """Test stock data validation."""
    # Invalid ticker (too long)
    response = client.post("/api/portfolio/stocks", json={
        "ticker": "VERYLONGTICKER",
        "quantity": 10.0,
        "average_buy_price": 100.0
    }, headers=auth_headers)
    assert response.status_code == 422
    
    # Invalid quantity (negative)
    response = client.post("/api/portfolio/stocks", json={
        "ticker": "AAPL",
        "quantity": -5.0,
        "average_buy_price": 100.0
    }, headers=auth_headers)
    assert response.status_code == 422
    
    # Invalid price (zero)
    response = client.post("/api/portfolio/stocks", json={
        "ticker": "AAPL",
        "quantity": 10.0,
        "average_buy_price": 0.0
    }, headers=auth_headers)
    assert response.status_code == 422


def test_unauthorized_access(client: TestClient):
    """Test that protected endpoints require authentication."""
    # Try to access portfolio without authentication
    response = client.get("/api/portfolio/stocks")
    assert response.status_code == 401
    
    # Try to access user info without authentication
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    
    # Try to access admin endpoint without authentication
    response = client.get("/api/admin/users")
    assert response.status_code == 401


def test_invalid_token(client: TestClient):
    """Test invalid token handling."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 401


@pytest.mark.parametrize("endpoint", [
    "/api/portfolio/stocks",
    "/api/auth/me",
    "/api/system/status"
])
def test_api_endpoints_exist(client: TestClient, endpoint: str):
    """Test that API endpoints exist (may return auth error)."""
    response = client.get(endpoint)
    # Should not return 404 (endpoint exists)
    assert response.status_code != 404