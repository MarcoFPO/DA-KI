#!/usr/bin/env python3
"""
DA-KI Integrierte Anwendung
Kombiniert FastAPI Backend + Dash Frontend in einem Server
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.staticfiles import StaticFiles
import logging

# Import des FastAPI Backends
from src.main_improved import app as fastapi_app

# Import der Dash Frontend App
try:
    from src.frontend.dashboard_app import create_daki_dashboard_app
    
    # Erstelle Dash App
    dash_app = create_daki_dashboard_app(api_base_url="http://localhost:8000")
    
    # Integriere Dash in FastAPI
    fastapi_app.mount("/dashboard", WSGIMiddleware(dash_app.get_app().server))
    
    # Redirect root zu Dashboard
    @fastapi_app.get("/")
    async def redirect_to_dashboard():
        return {"message": "DA-KI API Server", "dashboard_url": "/dashboard", "api_docs": "/api/docs"}
    
    print("✅ Frontend erfolgreich integriert")
    
except Exception as e:
    print(f"⚠️ Frontend-Integration fehlgeschlagen: {e}")
    print("🔧 API läuft ohne Dashboard")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    print("🚀 Starte DA-KI Integrierte Anwendung...")
    print("📊 Dashboard: http://localhost:8000/dashboard")
    print("🔧 API Docs: http://localhost:8000/api/docs")
    print("💡 Health Check: http://localhost:8000/health/liveness")
    
    uvicorn.run(
        "src.main_integrated:fastapi_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )