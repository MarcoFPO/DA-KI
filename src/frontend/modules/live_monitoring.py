#!/usr/bin/env python3
"""
Live-Monitoring Modul - Migrierte Version für neue Plugin-Architektur
"""

import logging
from dash import html, dcc, Input, Output, State, callback_context
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class LiveMonitoringModule:
    """
    Live-Monitoring Modul
    Migriert für Integration mit neuer Plugin-basierter API
    """
    
    def __init__(self, dashboard_app):
        """
        Initialisiere Live-Monitoring Modul
        
        Args:
            dashboard_app: Referenz zur Haupt-Dashboard-App
        """
        self.dashboard_app = dashboard_app
        self.api_base_url = dashboard_app.api_base_url
        
        # Modul-Konfiguration
        self.config = {
            'max_positions': 10,
            'refresh_interval': 60,  # 60 Sekunden
            'alert_threshold': 5.0  # 5% Verlust-Schwelle
        }
        
        logger.info("Live-Monitoring Modul initialisiert")
    
    def create_content(self) -> html.Div:
        """
        Erstelle Haupt-Content für Live-Monitoring
        
        Returns:
            html.Div: Modul-Content
        """
        return html.Div([
            # Header
            html.Div([
                html.H2([
                    html.I(className="fas fa-chart-line", style={'marginRight': '10px'}),
                    "Live Portfolio-Monitoring"
                ], style={'color': '#27ae60', 'marginBottom': '10px'}),
                html.P("Echtzeit-Überwachung Ihres Portfolios mit automatischen Updates",
                      style={'color': '#7f8c8d', 'marginBottom': '20px'})
            ]),
            
            # Quick-Actions Panel
            self._create_quick_actions_panel(),
            
            # Portfolio-Übersicht
            html.Div(id='portfolio-summary-container', children=[
                self._create_loading_portfolio_display()
            ]),
            
            # Positionen-Tabelle
            html.Div(id='positions-table-container', children=[]),
            
            # Performance-Charts
            html.Div(id='performance-charts-container', children=[]),
            
            # Add Position Modal
            self._create_add_position_modal()
            
        ], style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '10px',
            'margin': '10px 0'
        })
    
    def _create_quick_actions_panel(self) -> html.Div:
        """Erstelle Quick-Actions Panel"""
        return html.Div([
            html.Div([
                html.H4("⚡ Quick Actions", style={'margin': 0, 'marginBottom': '15px'}),
                
                html.Div([
                    html.Button([
                        html.I(className="fas fa-plus"),
                        " Position hinzufügen"
                    ], id='add-position-btn', className='btn btn-success',
                       style={'marginRight': '10px'}),
                    
                    html.Button([
                        html.I(className="fas fa-sync-alt"),
                        " Portfolio aktualisieren"
                    ], id='refresh-portfolio-btn', className='btn btn-primary',
                       style={'marginRight': '10px'}),
                    
                    html.Button([
                        html.I(className="fas fa-chart-pie"),
                        " Rebalancing"
                    ], id='rebalance-btn', className='btn btn-warning',
                       style={'marginRight': '10px'}),
                    
                    html.Button([
                        html.I(className="fas fa-download"),
                        " Export"
                    ], id='export-portfolio-btn', className='btn btn-secondary')
                ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '10px'})
            ])
        ], style={
            'backgroundColor': '#f8f9fa',
            'padding': '15px',
            'borderRadius': '8px',
            'marginBottom': '20px'
        })
    
    def _create_loading_portfolio_display(self) -> html.Div:
        """Erstelle Loading-Anzeige für Portfolio"""
        return html.Div([
            html.Div([
                html.I(className="fas fa-chart-line fa-spin", 
                      style={'fontSize': '32px', 'color': '#27ae60', 'marginBottom': '10px'}),
                html.H4("Portfolio wird geladen...", style={'color': '#27ae60'}),
                html.P("Live-Daten werden von den Datenquellen abgerufen", 
                      style={'color': '#7f8c8d'})
            ], style={'textAlign': 'center'})
        ], style={
            'backgroundColor': '#eafaf1',
            'padding': '40px',
            'borderRadius': '8px',
            'border': '1px solid #27ae60'
        })
    
    def _create_portfolio_summary_cards(self, portfolio_data: Dict) -> html.Div:
        """
        Erstelle Portfolio-Zusammenfassungs-Karten
        
        Args:
            portfolio_data: Portfolio-Daten von API
            
        Returns:
            html.Div: Portfolio-Zusammenfassung
        """
        try:
            # Berechne Zusammenfassungs-Metriken
            total_positions = len(portfolio_data.get('stocks', []))
            total_investment = sum(stock.get('total_cost', 0) for stock in portfolio_data.get('stocks', []))
            total_value = sum(stock.get('current_value', 0) for stock in portfolio_data.get('stocks', []))
            total_pnl = total_value - total_investment
            total_pnl_percent = (total_pnl / total_investment * 100) if total_investment > 0 else 0
            
            # Farb-Coding für P&L
            pnl_color = '#27ae60' if total_pnl >= 0 else '#e74c3c'
            
            cards = [
                self._create_summary_card(
                    "Positionen",
                    str(total_positions),
                    "fas fa-list",
                    '#3498db'
                ),
                self._create_summary_card(
                    "Investiert",
                    f"€{total_investment:,.0f}",
                    "fas fa-euro-sign",
                    '#f39c12'
                ),
                self._create_summary_card(
                    "Aktueller Wert",
                    f"€{total_value:,.0f}",
                    "fas fa-chart-line",
                    '#9b59b6'
                ),
                self._create_summary_card(
                    "Gewinn/Verlust",
                    f"€{total_pnl:+,.0f} ({total_pnl_percent:+.1f}%)",
                    "fas fa-balance-scale",
                    pnl_color
                )
            ]
            
            return html.Div([
                html.H3("📊 Portfolio-Übersicht", style={'marginBottom': '15px'}),
                html.Div(cards, style={
                    'display': 'grid',
                    'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))',
                    'gap': '15px',
                    'marginBottom': '20px'
                })
            ])
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Portfolio-Zusammenfassung: {e}")
            return html.Div(f"Fehler: {str(e)}", style={'color': '#e74c3c'})
    
    def _create_summary_card(self, title: str, value: str, icon: str, color: str) -> html.Div:
        """Erstelle einzelne Zusammenfassungs-Karte"""
        return html.Div([
            html.Div([
                html.I(className=icon, style={'fontSize': '28px', 'color': color}),
                html.Div([
                    html.H3(value, style={'margin': 0, 'color': color, 'fontSize': '20px'}),
                    html.P(title, style={'margin': 0, 'color': '#7f8c8d', 'fontSize': '14px'})
                ], style={'marginLeft': '15px'})
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '8px',
            'border': f'2px solid {color}',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        })
    
    def _create_positions_table(self, portfolio_data: Dict) -> html.Div:
        """
        Erstelle Positionen-Tabelle
        
        Args:
            portfolio_data: Portfolio-Daten
            
        Returns:
            html.Div: Positionen-Tabelle
        """
        stocks = portfolio_data.get('stocks', [])
        
        if not stocks:
            return self._create_empty_portfolio_display()
        
        try:
            # Tabellen-Header
            header = html.Thead([
                html.Tr([
                    html.Th("Ticker", style=self._get_header_style()),
                    html.Th("Name", style=self._get_header_style()),
                    html.Th("Anzahl", style=self._get_header_style()),
                    html.Th("Ø Einkauf", style=self._get_header_style()),
                    html.Th("Aktuell", style=self._get_header_style()),
                    html.Th("Wert", style=self._get_header_style()),
                    html.Th("G/V", style=self._get_header_style()),
                    html.Th("G/V %", style=self._get_header_style()),
                    html.Th("Aktionen", style=self._get_header_style())
                ])
            ])
            
            # Tabellen-Zeilen
            rows = []
            for stock in stocks:
                pnl = stock.get('current_value', 0) - stock.get('total_cost', 0)
                pnl_percent = (pnl / stock.get('total_cost', 1)) * 100
                pnl_color = '#27ae60' if pnl >= 0 else '#e74c3c'
                
                row = html.Tr([
                    html.Td(stock.get('ticker', 'N/A'), style={'fontWeight': 'bold'}),
                    html.Td(stock.get('company_name', 'Unknown')[:25]),
                    html.Td(stock.get('quantity', 0)),
                    html.Td(f"€{stock.get('average_price', 0):.2f}"),
                    html.Td(f"€{stock.get('current_price', 0):.2f}"),
                    html.Td(f"€{stock.get('current_value', 0):.0f}"),
                    html.Td(f"€{pnl:+.0f}", style={'color': pnl_color}),
                    html.Td(f"{pnl_percent:+.1f}%", style={'color': pnl_color}),
                    html.Td([
                        html.Button("📊", id={'type': 'view-details-btn', 'ticker': stock.get('ticker')},
                                  title="Details anzeigen", className='btn-small'),
                        html.Button("✏️", id={'type': 'edit-position-btn', 'ticker': stock.get('ticker')},
                                  title="Position bearbeiten", className='btn-small'),
                        html.Button("🗑️", id={'type': 'delete-position-btn', 'ticker': stock.get('ticker')},
                                  title="Position löschen", className='btn-small btn-danger')
                    ])
                ])
                rows.append(row)
            
            tbody = html.Tbody(rows)
            
            return html.Div([
                html.H3("📋 Aktuelle Positionen", style={'marginBottom': '15px'}),
                html.Table([header, tbody], style={
                    'width': '100%',
                    'borderCollapse': 'collapse',
                    'backgroundColor': 'white'
                })
            ])
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Positionen-Tabelle: {e}")
            return html.Div(f"Tabellen-Fehler: {str(e)}", style={'color': '#e74c3c'})
    
    def _get_header_style(self) -> Dict[str, str]:
        """Hole Header-Styling für Tabelle"""
        return {
            'backgroundColor': '#27ae60',
            'color': 'white',
            'padding': '12px 8px',
            'textAlign': 'left',
            'fontSize': '12px'
        }
    
    def _create_empty_portfolio_display(self) -> html.Div:
        """Erstelle Anzeige für leeres Portfolio"""
        return html.Div([
            html.I(className="fas fa-wallet", 
                  style={'fontSize': '48px', 'color': '#bdc3c7', 'marginBottom': '15px'}),
            html.H4("Portfolio ist leer", style={'color': '#7f8c8d'}),
            html.P("Fügen Sie Ihre erste Position hinzu, um mit dem Monitoring zu beginnen."),
            html.Button([
                html.I(className="fas fa-plus"),
                " Erste Position hinzufügen"
            ], id='add-first-position-btn', className='btn btn-primary')
        ], style={
            'textAlign': 'center',
            'backgroundColor': '#f8f9fa',
            'padding': '60px',
            'borderRadius': '8px',
            'border': '2px dashed #bdc3c7'
        })
    
    def _create_add_position_modal(self) -> html.Div:
        """Erstelle Add Position Modal"""
        return html.Div([
            html.Div([
                html.Div([
                    html.H4("📊 Position hinzufügen", style={'margin': 0}),
                    html.Button("×", id='close-add-modal-btn', 
                              style={'border': 'none', 'background': 'none', 'fontSize': '24px'})
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}),
                
                html.Hr(),
                
                # Formular
                html.Div([
                    html.Div([
                        html.Label("Ticker-Symbol:", style={'fontWeight': 'bold'}),
                        dcc.Input(
                            id='add-ticker-input',
                            type='text',
                            placeholder='z.B. SAP, ADBE, MSFT',
                            style={'width': '100%', 'padding': '8px', 'marginBottom': '10px'}
                        )
                    ]),
                    
                    html.Div([
                        html.Label("Anzahl Aktien:", style={'fontWeight': 'bold'}),
                        dcc.Input(
                            id='add-quantity-input',
                            type='number',
                            min=1,
                            placeholder='Anzahl',
                            style={'width': '100%', 'padding': '8px', 'marginBottom': '10px'}
                        )
                    ]),
                    
                    html.Div([
                        html.Label("Einkaufspreis (€):", style={'fontWeight': 'bold'}),
                        dcc.Input(
                            id='add-price-input',
                            type='number',
                            min=0,
                            step=0.01,
                            placeholder='Preis pro Aktie',
                            style={'width': '100%', 'padding': '8px', 'marginBottom': '20px'}
                        )
                    ]),
                    
                    html.Div([
                        html.Button([
                            html.I(className="fas fa-plus"),
                            " Position hinzufügen"
                        ], id='confirm-add-position-btn', className='btn btn-success',
                           style={'marginRight': '10px'}),
                        
                        html.Button("Abbrechen", id='cancel-add-position-btn', 
                                  className='btn btn-secondary')
                    ])
                ])
                
            ], style={
                'backgroundColor': 'white',
                'padding': '20px',
                'borderRadius': '8px',
                'maxWidth': '500px',
                'width': '90%'
            })
        ], id='add-position-modal', style={
            'position': 'fixed',
            'top': 0,
            'left': 0,
            'width': '100%',
            'height': '100%',
            'backgroundColor': 'rgba(0,0,0,0.5)',
            'display': 'none',
            'alignItems': 'center',
            'justifyContent': 'center',
            'zIndex': 1000
        })
    
    def setup_callbacks(self):
        """Setup Module-spezifische Callbacks"""
        
        @self.dashboard_app.app.callback(
            [Output('portfolio-summary-container', 'children'),
             Output('positions-table-container', 'children')],
            [Input('refresh-portfolio-btn', 'n_clicks'),
             Input('data-refresh-interval', 'n_intervals')]
        )
        def refresh_portfolio_data(refresh_clicks, interval_clicks):
            """Aktualisiere Portfolio-Daten"""
            try:
                # API-Call für Portfolio-Daten (ohne Auth für Demo)
                response = self.dashboard_app.make_api_call("/api/portfolio/stocks")
                
                if "error" in response:
                    return (html.Div(f"Fehler: {response['error']}", style={'color': '#e74c3c'}), "")
                
                # Portfolio-Daten verarbeiten
                portfolio_summary = self._create_portfolio_summary_cards({'stocks': response})
                positions_table = self._create_positions_table({'stocks': response})
                
                return portfolio_summary, positions_table
                
            except Exception as e:
                logger.error(f"Fehler beim Aktualisieren der Portfolio-Daten: {e}")
                return (html.Div(f"Update-Fehler: {str(e)}", style={'color': '#e74c3c'}), "")
        
        @self.dashboard_app.app.callback(
            Output('add-position-modal', 'style'),
            [Input('add-position-btn', 'n_clicks'),
             Input('add-first-position-btn', 'n_clicks'),
             Input('close-add-modal-btn', 'n_clicks'),
             Input('cancel-add-position-btn', 'n_clicks')]
        )
        def toggle_add_position_modal(add_clicks, add_first_clicks, close_clicks, cancel_clicks):
            """Toggle Add Position Modal"""
            ctx = callback_context
            if not ctx.triggered:
                return {'display': 'none'}
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id in ['add-position-btn', 'add-first-position-btn']:
                return {
                    'position': 'fixed',
                    'top': 0,
                    'left': 0,
                    'width': '100%',
                    'height': '100%',
                    'backgroundColor': 'rgba(0,0,0,0.5)',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'zIndex': 1000
                }
            else:
                return {'display': 'none'}


# Export
__all__ = ['LiveMonitoringModule']