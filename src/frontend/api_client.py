#!/usr/bin/env python3
"""
DA-KI Frontend API Client
Ersetzt direkte Service-Imports durch API-Calls
"""

import requests
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DAKIApiClient:
    """
    API Client für Frontend-Backend Kommunikation
    Ersetzt direkte Service-Imports
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        
    def set_auth_token(self, token: str):
        """Setze JWT-Token für authentifizierte Requests"""
        self.auth_token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
    def _make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """
        Zentrale Request-Methode mit Error-Handling
        
        Args:
            method: HTTP-Methode (GET, POST, PUT, DELETE)
            endpoint: API-Endpoint (z.B. "/api/portfolio/stocks")
            data: Request-Daten
            
        Returns:
            dict: API-Response oder Error-Dict
        """
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method == "GET":
                response = self.session.get(url, timeout=10)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=10)
            elif method == "PUT":
                response = self.session.put(url, json=data, timeout=10)
            elif method == "DELETE":
                response = self.session.delete(url, timeout=10)
            else:
                return {"error": f"Unsupported method: {method}"}
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {"error": f"API Error {response.status_code}: {response.text}"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API Request Fehler: {e}")
            return {"error": f"Verbindungsfehler: {str(e)}"}
        except Exception as e:
            logger.error(f"Unerwarteter Fehler: {e}")
            return {"error": f"Unerwarteter Fehler: {str(e)}"}
    
    # ================== AUTHENTICATION ==================
    
    def login(self, username: str, password: str) -> dict:
        """
        User-Login
        
        Returns:
            dict: Token-Daten oder Fehler
        """
        data = {"username": username, "password": password}
        response = requests.post(
            f"{self.base_url}/api/auth/token",
            data=data,  # Form-encoded für OAuth2
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            self.set_auth_token(token_data["access_token"])
            return token_data
        else:
            return {"error": f"Login fehlgeschlagen: {response.text}"}
    
    def register(self, username: str, password: str) -> dict:
        """User-Registrierung"""
        data = {"username": username, "password": password}
        return self._make_request("POST", "/api/auth/register", data)
    
    def get_current_user(self) -> dict:
        """Aktuelle User-Informationen"""
        return self._make_request("GET", "/api/auth/me")
    
    # ================== PORTFOLIO MANAGEMENT ==================
    
    def get_portfolio_stocks(self) -> dict:
        """Hole alle Aktien im Portfolio"""
        return self._make_request("GET", "/api/portfolio/stocks")
    
    def add_stock_to_portfolio(self, ticker: str, quantity: int, average_price: float) -> dict:
        """Füge Aktie zum Portfolio hinzu"""
        data = {
            "ticker": ticker,
            "quantity": quantity,
            "average_buy_price": average_price
        }
        return self._make_request("POST", "/api/portfolio/stocks", data)
    
    def update_stock_in_portfolio(self, stock_id: int, **kwargs) -> dict:
        """Update Aktie im Portfolio"""
        return self._make_request("PUT", f"/api/portfolio/stocks/{stock_id}", kwargs)
    
    def delete_stock_from_portfolio(self, stock_id: int) -> dict:
        """Lösche Aktie aus Portfolio"""
        return self._make_request("DELETE", f"/api/portfolio/stocks/{stock_id}")
    
    # ================== ANALYSIS ==================
    
    def start_analysis(self, tickers: List[str], analysis_type: str = "growth_prediction") -> dict:
        """
        Starte Stock-Analyse
        
        Args:
            tickers: Liste von Ticker-Symbolen
            analysis_type: Art der Analyse
            
        Returns:
            dict: Analyse-Ergebnisse
        """
        data = {
            "tickers": tickers,
            "analysis_type": analysis_type
        }
        return self._make_request("POST", "/api/analysis/start", data)
    
    def get_analysis_history(self, ticker: str = None) -> dict:
        """Hole Analyse-Historie"""
        endpoint = "/api/analysis/history"
        if ticker:
            endpoint += f"?ticker={ticker}"
        return self._make_request("GET", endpoint)
    
    # ================== SYSTEM STATUS ==================
    
    def get_system_status(self) -> dict:
        """Hole System-Status"""
        return self._make_request("GET", "/api/system/status")
    
    def health_check(self) -> dict:
        """Health Check"""
        return self._make_request("GET", "/health/liveness")
    
    def readiness_check(self) -> dict:
        """Readiness Check"""
        return self._make_request("GET", "/health/readiness")
    
    # ================== MOCK DATA (für Development) ==================
    
    def get_mock_portfolio_data(self) -> dict:
        """
        Mock Portfolio-Daten für Development
        Falls Backend nicht verfügbar
        """
        return {
            "stocks": [
                {
                    "id": 1,
                    "ticker": "SAP",
                    "company_name": "SAP SE",
                    "quantity": 10,
                    "average_buy_price": 120.0,
                    "current_price": 125.5,
                    "total_cost": 1200.0,
                    "current_value": 1255.0
                },
                {
                    "id": 2,
                    "ticker": "ADBE",
                    "company_name": "Adobe Inc.",
                    "quantity": 5,
                    "average_buy_price": 450.0,
                    "current_price": 465.2,
                    "total_cost": 2250.0,
                    "current_value": 2326.0
                }
            ]
        }
    
    def get_mock_analysis_results(self) -> List[dict]:
        """Mock Analyse-Ergebnisse"""
        return [
            {
                "ticker": "SAP",
                "company_name": "SAP SE",
                "growth_score": 85.2,
                "current_price": 125.5,
                "predicted_return": 12.5,
                "confidence_level": 0.8
            },
            {
                "ticker": "ADBE", 
                "company_name": "Adobe Inc.",
                "growth_score": 92.1,
                "current_price": 465.2,
                "predicted_return": 18.3,
                "confidence_level": 0.9
            }
        ]


# Singleton für globale Verwendung
api_client = DAKIApiClient()

def get_api_client() -> DAKIApiClient:
    """Hole globalen API Client"""
    return api_client


# Export
__all__ = ['DAKIApiClient', 'get_api_client', 'api_client']