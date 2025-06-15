#!/usr/bin/env python3
"""
Dashboard Orchestrator - Modulare Dashboard-Architektur
Koordiniert alle isolierten Module mit definierten Schnittstellen
"""

import dash
from dash import dcc, html, Input, Output, State, callback, callback_context
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import aller isolierten Module
from ki_wachstumsprognose_module import (
    create_wachstumsprognose_instance,
    get_wachstumsprognose_data_interface
)
from live_monitoring_module import (
    create_live_monitoring_instance,
    get_data_interface as get_live_monitoring_interface
)
from frontend_layout_module import (
    create_frontend_layout_instance,
    get_layout_data_interface,
    SECTION_STYLES
)
from frontend_tabelle_module import (
    create_frontend_tabelle_instance,
    get_tabelle_data_interface,
    create_action_button_integration
)
from frontend_callback_module import (
    create_frontend_callback_instance
)

class DashboardOrchestrator:
    """Hauptklasse für modulares Dashboard-Management"""
    
    def __init__(self, app_title: str = "🚀 DA-KI Dashboard"):
        # Dash App initialisieren
        self.app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
        self.app.title = app_title
        
        # Module-Instanzen (isoliert)
        self.wachstumsprognose = create_wachstumsprognose_instance()
        self.wachstums_interface = get_wachstumsprognose_data_interface()
        self.live_monitoring = create_live_monitoring_instance()
        self.live_monitoring_interface = get_live_monitoring_interface()
        self.frontend_layout = create_frontend_layout_instance(app_title)
        self.layout_interface = get_layout_data_interface()
        self.frontend_tabelle = create_frontend_tabelle_instance()
        self.tabelle_interface = get_tabelle_data_interface()
        
        # Action-Button Integration (Dependency Injection)
        self.action_integration = create_action_button_integration(self.live_monitoring)
        self.frontend_tabelle.set_action_button_interface(self.action_integration)
        
        # Callback-Modul (isoliert)
        self.frontend_callbacks = create_frontend_callback_instance(self.app)
        
        # Initiale Daten laden
        self.aktien_daten = self.wachstumsprognose.get_aktien_daten()
        
        # Layout und Callbacks initialisieren
        self._setup_layout()
        self._setup_callbacks()
    
    # ================== LAYOUT ORCHESTRATION ==================
    
    def _setup_layout(self):
        """Private: Setup des gesamten Dashboard-Layouts"""
        # Header
        header = self.frontend_layout.create_main_header()
        
        # Action Bar
        action_bar = self.frontend_layout.create_action_bar()
        
        # Status Container
        status_container = self.frontend_layout.create_status_container()
        
        # KI-Wachstumsprognose Section
        wachstums_container = self._create_wachstumsprognose_section_for_layout()
        
        # Charts Section
        charts_container = self._create_charts_section_for_layout()
        
        # Enhanced Tabelle Section  
        tabelle_container = self._create_enhanced_tabelle_section_for_layout()
        
        # Live-Monitoring Section
        monitoring_container = self._create_live_monitoring_section()
        
        # Modal Dialog
        modal_dialog = self.live_monitoring.create_modal_dialog()
        
        # Footer
        footer = self.frontend_layout.create_footer()
        
        # Haupt-Layout zusammensetzen
        layout_children = [
            header,
            action_bar,
            status_container,
            wachstums_container,
            charts_container,
            tabelle_container,
            monitoring_container,
            modal_dialog,
            footer
        ]
        
        self.app.layout = self.frontend_layout.create_main_layout_container(layout_children)
    
    def _create_wachstumsprognose_section_for_layout(self) -> html.Div:
        """Private: Erstelle KI-Wachstumsprognose Section für initiales Layout"""
        wachstums_content = self.wachstumsprognose.create_wachstumsprognose_container(self.aktien_daten)
        
        return html.Div(
            id='wachstumsprognose-container', 
            children=wachstums_content
        )
    
    def _create_charts_section_for_layout(self) -> html.Div:
        """Private: Erstelle Charts Section für initiales Layout"""
        charts_content = self.wachstumsprognose.create_charts_container(self.aktien_daten)
        
        return html.Div(
            id='charts-container',
            children=charts_content
        )
    
    def _create_enhanced_tabelle_section_for_layout(self) -> html.Div:
        """Private: Erstelle Enhanced Tabelle Section für initiales Layout"""
        enhanced_tabelle = self.frontend_tabelle.create_wachstumsprognose_tabelle_mit_actions(self.aktien_daten)
        
        tabelle_mit_container = self.frontend_tabelle.create_table_container(
            enhanced_tabelle,
            "📋 Detaillierte Wachstumsprognose mit Firmenprofilen"
        )
        
        return html.Div(
            id='prognose-tabelle-section',
            children=tabelle_mit_container,
            style={
                'backgroundColor': '#ffffff',
                'padding': '20px',
                'borderRadius': '10px',
                'marginBottom': '20px',
                'border': '2px solid #e74c3c'
            }
        )
    
    def _create_live_monitoring_section(self) -> html.Div:
        """Private: Erstelle Live-Monitoring Section"""
        monitoring_content = self.live_monitoring.create_live_monitoring_dashboard()
        
        return self.frontend_layout.create_section_container(
            "💼 Live-Monitoring Dashboard",
            monitoring_content,
            SECTION_STYLES['live_monitoring']['background_color'],
            SECTION_STYLES['live_monitoring']['border_color']
        )
    
    # ================== CALLBACK ORCHESTRATION ==================
    
    def _setup_callbacks(self):
        """Private: Setup aller modularen Callbacks über Callback-Modul"""
        self.frontend_callbacks.setup_all_callbacks(self)
    
    # ================== HELPER METHODS FOR CALLBACK MODULE ==================
    
    def _create_wachstumsprognose_section(self, aktien_daten: List[Dict]) -> html.Div:
        """Helper: Erstelle KI-Wachstumsprognose Section für Callback"""
        wachstums_content = self.wachstumsprognose.create_wachstumsprognose_container(aktien_daten)
        return html.Div(id='wachstumsprognose-container', children=wachstums_content)
    
    def _create_charts_section(self, aktien_daten: List[Dict]) -> html.Div:
        """Helper: Erstelle Charts Section für Callback"""
        charts_content = self.wachstumsprognose.create_charts_container(aktien_daten)
        return html.Div(id='charts-container', children=charts_content)
    
    def _create_enhanced_tabelle_section(self, aktien_daten: List[Dict]) -> html.Div:
        """Helper: Erstelle Enhanced Tabelle Section für Callback"""
        enhanced_tabelle = self.frontend_tabelle.create_wachstumsprognose_tabelle_mit_actions(aktien_daten)
        tabelle_mit_container = self.frontend_tabelle.create_table_container(
            enhanced_tabelle,
            "📋 Detaillierte Wachstumsprognose mit Firmenprofilen"
        )
        
        return html.Div(
            id='prognose-tabelle-section',
            children=tabelle_mit_container,
            style={
                'backgroundColor': '#ffffff',
                'padding': '20px',
                'borderRadius': '10px',
                'marginBottom': '20px',
                'border': '2px solid #e74c3c'
            }
        )
    
    def _update_portfolio_summary(self, portfolio_data: Dict) -> html.Div:
        """Private: Update Portfolio-Zusammenfassung"""
        return html.Div([
            html.Div([
                html.H4(str(portfolio_data['position_count']), style={'margin': 0, 'color': '#3498db'}),
                html.P("Positionen", style={'margin': 0, 'fontSize': '12px'})
            ], style={
                'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#ebf3fd',
                'borderRadius': '10px', 'width': '22%', 'display': 'inline-block', 'margin': '1%'
            }),
            html.Div([
                html.H4(f"€{portfolio_data['total_investment']:,.0f}", style={'margin': 0, 'color': '#27ae60'}),
                html.P("Investiert", style={'margin': 0, 'fontSize': '12px'})
            ], style={
                'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#eafaf1',
                'borderRadius': '10px', 'width': '22%', 'display': 'inline-block', 'margin': '1%'
            }),
            html.Div([
                html.H4(f"€{portfolio_data['total_value']:,.0f}", style={'margin': 0, 'color': '#f39c12'}),
                html.P("Aktueller Wert", style={'margin': 0, 'fontSize': '12px'})
            ], style={
                'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#fef9e7',
                'borderRadius': '10px', 'width': '22%', 'display': 'inline-block', 'margin': '1%'
            }),
            html.Div([
                html.H4(f"{portfolio_data['avg_score']:.1f}/100", style={'margin': 0, 'color': '#e74c3c'}),
                html.P("Ø KI-Score", style={'margin': 0, 'fontSize': '12px'})
            ], style={
                'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#fdf2f2',
                'borderRadius': '10px', 'width': '22%', 'display': 'inline-block', 'margin': '1%'
            })
        ])
    
    def _update_portfolio_positions(self, portfolio_data: Dict) -> html.Table:
        """Private: Update Portfolio-Positionen"""
        zeilen = []
        for position in portfolio_data['positions']:
            current_value = position['shares'] * position['current_price']
            profit_loss = current_value - position['investment']
            profit_loss_percent = (profit_loss / position['investment']) * 100 if position['investment'] > 0 else 0
            
            zeile = html.Tr([
                html.Td(position['symbol'], style={'fontWeight': 'bold'}),
                html.Td(position['name'][:20]),
                html.Td(str(position['shares'])),
                html.Td(f"€{position['current_price']:.2f}"),
                html.Td(f"€{position['investment']:.0f}"),
                html.Td(f"€{current_value:.0f}"),
                html.Td(f"{profit_loss:+.0f}€ ({profit_loss_percent:+.1f}%)", 
                       style={'color': '#27ae60' if profit_loss >= 0 else '#e74c3c'}),
                html.Td(position['added_date'], style={'fontSize': '11px'}),
                html.Td([
                    html.Button(
                        '🗑️',
                        id={'type': 'remove-position-btn', 'index': position['id']},
                        style={
                            'backgroundColor': '#e74c3c',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '3px',
                            'padding': '5px 8px',
                            'cursor': 'pointer'
                        }
                    )
                ])
            ])
            zeilen.append(zeile)
        
        header_style = {'padding': '8px', 'backgroundColor': '#3498db', 'color': 'white'}
        
        return html.Table([
            html.Thead([
                html.Tr([
                    html.Th("Symbol", style=header_style),
                    html.Th("Name", style=header_style),
                    html.Th("Anzahl", style=header_style),
                    html.Th("Kurs", style=header_style),
                    html.Th("Investiert", style=header_style),
                    html.Th("Wert", style=header_style),
                    html.Th("Gewinn/Verlust", style=header_style),
                    html.Th("Hinzugefügt", style=header_style),
                    html.Th("Aktion", style=header_style)
                ])
            ]),
            html.Tbody(zeilen)
        ], style={'width': '100%', 'borderCollapse': 'collapse', 'backgroundColor': 'white'})
    
    # ================== PUBLIC INTERFACE ==================
    
    def run_server(self, debug: bool = False, host: str = '0.0.0.0', port: int = 8054):
        """
        SCHNITTSTELLE: Starte Dashboard-Server
        
        Input:
            debug (bool) - Debug-Modus
            host (str) - Server-Host
            port (int) - Server-Port
        """
        print("🚀 Starte Modulares DA-KI Dashboard (Vollständig isolierte Architektur)...")
        print(f"📊 URL: http://10.1.1.110:{port}")
        print("🔧 Modulare Frontend-Architektur:")
        print("   - Frontend Layout Module (isoliert)")
        print("   - Frontend Tabelle Module (isoliert)")  
        print("   - KI-Wachstumsprognose Module (isoliert)")
        print("   - Live-Monitoring Module (isoliert)")
        print("   - Dashboard Orchestrator (koordiniert)")
        print("⚠️  VERBOTEN: Verwendung von Loopback-Adressen (127.0.0.1, localhost)")
        print("⚠️  NUR IP 10.1.1.110 und Port 8054 verwenden!")
        
        self.app.run(debug=debug, host=host, port=port)
    
    def get_app(self):
        """Gebe Dash-App-Instanz zurück (für externe Verwendung)"""
        return self.app

# ================== EXPORT ==================

def create_dashboard_orchestrator(app_title: str = "🚀 DA-KI Dashboard"):
    """Factory-Funktion für Dashboard-Orchestrator"""
    return DashboardOrchestrator(app_title)