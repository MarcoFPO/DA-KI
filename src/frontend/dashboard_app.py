#!/usr/bin/env python3
"""
DA-KI Frontend Dashboard Application
Migrierter Dashboard-Orchestrator für neue Plugin-Architektur
"""

import dash
from dash import dcc, html, Input, Output, State, callback, callback_context
import plotly.graph_objs as go
import plotly.express as px
import requests
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Import der neuen Services
from src.services.analysis_service import AnalysisService
from src.services.portfolio_service import PortfolioService
from src.database.db_access_extended import DBAccessExtended
from src.config.config import Config

# Frontend Module
from .orchestrator import DashboardOrchestrator
from .modules.live_monitoring import LiveMonitoringModule
from .modules.ki_wachstumsprognose import KIWachstumsprognoseModule
from .components.layout_components import LayoutComponents

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DAKIDashboardApp:
    """
    Haupt-Dashboard-Anwendung für DA-KI
    Integriert alte modulare Architektur mit neuer Plugin-basierten API
    """
    
    def __init__(self, api_base_url: str = "http://localhost:8000", app_title: str = "🚀 DA-KI Dashboard v2.0"):
        # Dash App initialisieren
        self.app = dash.Dash(
            __name__, 
            external_stylesheets=[
                'https://codepen.io/chriddyp/pen/bWLwgP.css',
                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
            ]
        )
        self.app.title = app_title
        self.api_base_url = api_base_url
        
        # Services initialisieren
        try:
            self.db_access = DBAccessExtended()
            self.analysis_service = AnalysisService(self.db_access)
            self.portfolio_service = PortfolioService(self.db_access)
            logger.info("Services erfolgreich initialisiert")
        except Exception as e:
            logger.error(f"Fehler bei Service-Initialisierung: {e}")
            self.db_access = None
            self.analysis_service = None
            self.portfolio_service = None
        
        # Frontend-Module
        self.orchestrator = DashboardOrchestrator(self)
        self.live_monitoring = LiveMonitoringModule(self)
        self.ki_wachstumsprognose = KIWachstumsprognoseModule(self)
        self.layout_components = LayoutComponents()
        
        # Layout und Callbacks initialisieren
        self._setup_layout()
        self._setup_callbacks()
        
        logger.info("DA-KI Dashboard App erfolgreich initialisiert")
    
    def _setup_layout(self):
        """Setup des gesamten Dashboard-Layouts"""
        
        # Header
        header = self.layout_components.create_main_header()
        
        # Navigation Bar
        nav_bar = self.layout_components.create_navigation_bar()
        
        # Status Container
        status_container = self.layout_components.create_status_container()
        
        # Main Content Tabs
        main_content = self._create_main_content_tabs()
        
        # Footer
        footer = self.layout_components.create_footer()
        
        # Haupt-Layout zusammensetzen
        self.app.layout = html.Div([
            dcc.Store(id='auth-token-store', storage_type='session'),
            dcc.Store(id='user-data-store', storage_type='session'),
            dcc.Interval(id='data-refresh-interval', interval=60000, n_intervals=0),  # 60 Sekunden
            
            header,
            nav_bar,
            status_container,
            main_content,
            footer,
            
            # Modal für Notifications
            html.Div(id='notification-modal', children=[], style={'display': 'none'})
        ], style={
            'backgroundColor': '#f8f9fa',
            'minHeight': '100vh',
            'fontFamily': 'Arial, sans-serif'
        })
    
    def _create_main_content_tabs(self) -> html.Div:
        """Erstelle Haupt-Content mit Tabs"""
        return html.Div([
            dcc.Tabs(
                id='main-tabs',
                value='ki-wachstumsprognose',
                children=[
                    dcc.Tab(
                        label='🤖 KI-Wachstumsprognose',
                        value='ki-wachstumsprognose',
                        style={'padding': '6px', 'fontWeight': 'bold'},
                        selected_style={'padding': '6px', 'fontWeight': 'bold', 'backgroundColor': '#3498db', 'color': 'white'}
                    ),
                    dcc.Tab(
                        label='📊 Live-Monitoring',
                        value='live-monitoring',
                        style={'padding': '6px', 'fontWeight': 'bold'},
                        selected_style={'padding': '6px', 'fontWeight': 'bold', 'backgroundColor': '#27ae60', 'color': 'white'}
                    ),
                    dcc.Tab(
                        label='💰 Portfolio-Management',
                        value='portfolio-management',
                        style={'padding': '6px', 'fontWeight': 'bold'},
                        selected_style={'padding': '6px', 'fontWeight': 'bold', 'backgroundColor': '#e74c3c', 'color': 'white'}
                    ),
                    dcc.Tab(
                        label='🔧 Plugin-Manager',
                        value='plugin-manager',
                        style={'padding': '6px', 'fontWeight': 'bold'},
                        selected_style={'padding': '6px', 'fontWeight': 'bold', 'backgroundColor': '#9b59b6', 'color': 'white'}
                    )
                ]
            ),
            html.Div(id='tab-content', style={'padding': '20px'})
        ])
    
    def _setup_callbacks(self):
        """Setup aller Dashboard-Callbacks"""
        
        @self.app.callback(
            Output('tab-content', 'children'),
            [Input('main-tabs', 'value')]
        )
        def render_tab_content(active_tab):
            """Rendere Content basierend auf aktivem Tab"""
            try:
                if active_tab == 'ki-wachstumsprognose':
                    return self.ki_wachstumsprognose.create_content()
                elif active_tab == 'live-monitoring':
                    return self.live_monitoring.create_content()
                elif active_tab == 'portfolio-management':
                    return self._create_portfolio_management_content()
                elif active_tab == 'plugin-manager':
                    return self._create_plugin_manager_content()
                else:
                    return html.Div("Tab nicht gefunden", style={'color': 'red'})
            except Exception as e:
                logger.error(f"Fehler beim Rendern von Tab {active_tab}: {e}")
                return html.Div(f"Fehler: {str(e)}", style={'color': 'red'})
        
        @self.app.callback(
            Output('status-container', 'children'),
            [Input('data-refresh-interval', 'n_intervals')]
        )
        def update_status_container(n_intervals):
            """Update Status-Container"""
            return self._get_system_status()
        
        # Weitere Callbacks von Modulen
        self.ki_wachstumsprognose.setup_callbacks()
        self.live_monitoring.setup_callbacks()
    
    def _create_portfolio_management_content(self) -> html.Div:
        """Erstelle Portfolio-Management Content"""
        return html.Div([
            html.H2("💰 Portfolio-Management", style={'color': '#e74c3c'}),
            html.Div([
                html.P("Portfolio-Management Features:"),
                html.Ul([
                    html.Li("Risiko-Management mit Stop-Loss"),
                    html.Li("Automatische Rebalancing-Algorithmen"),
                    html.Li("Compliance-Monitoring"),
                    html.Li("Performance-Analytics")
                ])
            ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px'})
        ])
    
    def _create_plugin_manager_content(self) -> html.Div:
        """Erstelle Plugin-Manager Content"""
        return html.Div([
            html.H2("🔧 Plugin-Manager", style={'color': '#9b59b6'}),
            html.Div([
                html.P("Verfügbare Datenquellen-Plugins:"),
                html.Div(id='plugin-status-cards'),
                html.Hr(),
                html.Button(
                    "🔄 Plugin-Status aktualisieren",
                    id='refresh-plugins-btn',
                    className='btn btn-primary',
                    style={'margin': '10px'}
                )
            ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px'})
        ])
    
    def _get_system_status(self) -> html.Div:
        """Hole aktuellen System-Status"""
        try:
            # API-Call für System-Status
            response = requests.get(f"{self.api_base_url}/api/system/status", timeout=5)
            if response.status_code == 200:
                status_data = response.json()
                return self.layout_components.create_status_cards(status_data)
            else:
                return html.Div("⚠️ API nicht erreichbar", style={'color': 'orange'})
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des System-Status: {e}")
            return html.Div("❌ System-Status nicht verfügbar", style={'color': 'red'})
    
    def make_api_call(self, endpoint: str, method: str = "GET", data: dict = None, auth_token: str = None) -> dict:
        """
        Zentrale API-Call Funktion
        
        Args:
            endpoint: API-Endpoint (z.B. "/api/portfolio/stocks")
            method: HTTP-Methode
            data: Request-Daten
            auth_token: JWT-Token für Authentifizierung
            
        Returns:
            dict: API-Response oder Fehler-Dict
        """
        try:
            url = f"{self.api_base_url}{endpoint}"
            headers = {'Content-Type': 'application/json'}
            
            if auth_token:
                headers['Authorization'] = f"Bearer {auth_token}"
            
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                return {"error": f"Unsupported method: {method}"}
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {"error": f"API Error {response.status_code}: {response.text}"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API-Call Fehler: {e}")
            return {"error": f"Verbindungsfehler: {str(e)}"}
        except Exception as e:
            logger.error(f"Unerwarteter Fehler: {e}")
            return {"error": f"Unerwarteter Fehler: {str(e)}"}
    
    def run_server(self, debug: bool = False, host: str = '0.0.0.0', port: int = 8054):
        """
        Starte Dashboard-Server
        
        Args:
            debug: Debug-Modus
            host: Server-Host
            port: Server-Port
        """
        print("🚀 Starte DA-KI Dashboard v2.0 (Plugin-integriert)...")
        print(f"📊 Dashboard URL: http://10.1.1.110:{port}")
        print(f"🔌 API Backend: {self.api_base_url}")
        print("🏗️ Neue Architektur:")
        print("   - Plugin-basierte Datenquellen")
        print("   - JWT-Authentifizierung")
        print("   - Modulare Frontend-Architektur")
        print("   - Live-API-Integration")
        print("⚠️  Backend muss unter http://localhost:8000 laufen!")
        
        self.app.run(debug=debug, host=host, port=port)
    
    def get_app(self):
        """Gebe Dash-App-Instanz zurück"""
        return self.app


# Factory-Funktion
def create_daki_dashboard_app(api_base_url: str = "http://localhost:8000") -> DAKIDashboardApp:
    """Factory-Funktion für DA-KI Dashboard App"""
    return DAKIDashboardApp(api_base_url)


# Main Entry Point
if __name__ == "__main__":
    # Konfiguration laden
    try:
        Config.load_secrets()
    except Exception as e:
        logger.warning(f"Konnte Konfiguration nicht laden: {e}")
    
    # Dashboard erstellen und starten
    dashboard_app = create_daki_dashboard_app()
    dashboard_app.run_server(debug=True, host='0.0.0.0', port=8054)