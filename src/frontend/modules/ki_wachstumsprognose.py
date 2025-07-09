#!/usr/bin/env python3
"""
KI-Wachstumsprognose Modul - Migrierte Version für neue Plugin-Architektur
"""

import logging
from dash import html, dcc, Input, Output, State, callback_context
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class KIWachstumsprognoseModule:
    """
    KI-Wachstumsprognose Modul
    Migriert für Integration mit neuer Plugin-basierter API
    """
    
    def __init__(self, dashboard_app):
        """
        Initialisiere KI-Wachstumsprognose Modul
        
        Args:
            dashboard_app: Referenz zur Haupt-Dashboard-App
        """
        self.dashboard_app = dashboard_app
        self.api_base_url = dashboard_app.api_base_url
        
        # Modul-Konfiguration
        self.config = {
            'max_stocks_display': 10,
            'refresh_interval': 300,  # 5 Minuten
            'confidence_threshold': 0.7
        }
        
        logger.info("KI-Wachstumsprognose Modul initialisiert")
    
    def create_content(self) -> html.Div:
        """
        Erstelle Haupt-Content für KI-Wachstumsprognose
        
        Returns:
            html.Div: Modul-Content
        """
        return html.Div([
            # Header
            html.Div([
                html.H2([
                    html.I(className="fas fa-robot", style={'marginRight': '10px'}),
                    "KI-Wachstumsprognose"
                ], style={'color': '#3498db', 'marginBottom': '10px'}),
                html.P("Automatisierte Aktienanalyse mit Machine Learning und Plugin-Datenquellen",
                      style={'color': '#7f8c8d', 'marginBottom': '20px'})
            ]),
            
            # Kontroll-Panel
            self._create_control_panel(),
            
            # Ergebnisse-Container
            html.Div(id='ki-results-container', children=[
                self._create_loading_display()
            ]),
            
            # Charts-Container  
            html.Div(id='ki-charts-container', children=[]),
            
            # Detaillierte Tabelle
            html.Div(id='ki-table-container', children=[])
            
        ], style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '10px',
            'margin': '10px 0'
        })
    
    def _create_control_panel(self) -> html.Div:
        """Erstelle Kontroll-Panel"""
        return html.Div([
            html.Div([
                html.Label("Analyse-Parameter:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                
                html.Div([
                    html.Div([
                        html.Label("Markt-Segment:", style={'fontSize': '12px'}),
                        dcc.Dropdown(
                            id='market-segment-dropdown',
                            options=[
                                {'label': '🇩🇪 DAX (Top 40)', 'value': 'dax'},
                                {'label': '📈 MDAX (Mid Cap)', 'value': 'mdax'},
                                {'label': '🔍 SDAX (Small Cap)', 'value': 'sdax'},
                                {'label': '🌟 Alle deutschen Aktien', 'value': 'all'}
                            ],
                            value='dax',
                            style={'width': '100%'}
                        )
                    ], style={'width': '23%', 'display': 'inline-block', 'marginRight': '2%'}),
                    
                    html.Div([
                        html.Label("Zeitraum:", style={'fontSize': '12px'}),
                        dcc.Dropdown(
                            id='timeframe-dropdown',
                            options=[
                                {'label': '1 Monat', 'value': '1m'},
                                {'label': '3 Monate', 'value': '3m'},
                                {'label': '6 Monate', 'value': '6m'},
                                {'label': '1 Jahr', 'value': '1y'}
                            ],
                            value='3m',
                            style={'width': '100%'}
                        )
                    ], style={'width': '23%', 'display': 'inline-block', 'marginRight': '2%'}),
                    
                    html.Div([
                        html.Label("KI-Modell:", style={'fontSize': '12px'}),
                        dcc.Dropdown(
                            id='model-dropdown',
                            options=[
                                {'label': '🤖 5-Faktor-Scoring', 'value': 'five_factor'},
                                {'label': '📊 Technical Analysis', 'value': 'technical'},
                                {'label': '📰 Sentiment + Technical', 'value': 'hybrid'},
                                {'label': '🧠 Neural Network', 'value': 'neural'}
                            ],
                            value='five_factor',
                            style={'width': '100%'}
                        )
                    ], style={'width': '23%', 'display': 'inline-block', 'marginRight': '2%'}),
                    
                    html.Div([
                        html.Label("Aktionen:", style={'fontSize': '12px'}),
                        html.Div([
                            html.Button([
                                html.I(className="fas fa-play"),
                                " Analyse starten"
                            ], id='start-analysis-btn', className='btn btn-primary',
                               style={'width': '100%', 'marginBottom': '5px'}),
                            
                            html.Button([
                                html.I(className="fas fa-download"),
                                " Export"
                            ], id='export-results-btn', className='btn btn-secondary',
                               style={'width': '100%', 'fontSize': '12px'})
                        ])
                    ], style={'width': '23%', 'display': 'inline-block'})
                ])
            ], style={'marginBottom': '20px'})
        ], style={
            'backgroundColor': '#f8f9fa',
            'padding': '15px',
            'borderRadius': '8px',
            'marginBottom': '20px'
        })
    
    def _create_loading_display(self) -> html.Div:
        """Erstelle Loading-Anzeige"""
        return html.Div([
            html.Div([
                html.I(className="fas fa-robot fa-spin", 
                      style={'fontSize': '32px', 'color': '#3498db', 'marginBottom': '10px'}),
                html.H4("KI-Analyse bereit", style={'color': '#3498db'}),
                html.P("Wählen Sie Parameter und starten Sie die Analyse", 
                      style={'color': '#7f8c8d'})
            ], style={'textAlign': 'center'})
        ], style={
            'backgroundColor': '#ebf3fd',
            'padding': '40px',
            'borderRadius': '8px',
            'border': '1px solid #3498db'
        })
    
    def _create_results_cards(self, analysis_results: List[Dict]) -> html.Div:
        """
        Erstelle Ergebnis-Karten
        
        Args:
            analysis_results: Analyse-Ergebnisse von API
            
        Returns:
            html.Div: Ergebnis-Karten
        """
        if not analysis_results:
            return self._create_no_results_display()
        
        cards = []
        for i, stock in enumerate(analysis_results[:10]):  # Top 10
            try:
                # Farb-Coding basierend auf Score
                score = float(stock.get('growth_score', 0))
                if score >= 80:
                    color = '#27ae60'  # Grün
                    icon = 'fas fa-arrow-up'
                elif score >= 60:
                    color = '#f39c12'  # Orange
                    icon = 'fas fa-arrow-right'
                else:
                    color = '#e74c3c'  # Rot
                    icon = 'fas fa-arrow-down'
                
                card = html.Div([
                    html.Div([
                        html.Div([
                            html.H3(f"#{i+1}", style={'margin': 0, 'color': color}),
                            html.I(className=icon, style={'fontSize': '20px', 'color': color})
                        ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}),
                        
                        html.H4(stock.get('ticker', 'N/A'), 
                               style={'margin': '10px 0 5px 0', 'color': '#2c3e50'}),
                        html.P(stock.get('company_name', 'Unbekannt')[:25] + "...", 
                              style={'margin': 0, 'fontSize': '12px', 'color': '#7f8c8d'}),
                        
                        html.Hr(style={'margin': '10px 0'}),
                        
                        html.Div([
                            html.Div([
                                html.Strong(f"{score:.1f}"),
                                html.Br(),
                                html.Small("KI-Score")
                            ], style={'textAlign': 'center', 'width': '33%'}),
                            
                            html.Div([
                                html.Strong(f"€{stock.get('current_price', 0):.2f}"),
                                html.Br(),
                                html.Small("Kurs")
                            ], style={'textAlign': 'center', 'width': '33%'}),
                            
                            html.Div([
                                html.Strong(f"{stock.get('predicted_return', 0):.1f}%"),
                                html.Br(),
                                html.Small("Prognose")
                            ], style={'textAlign': 'center', 'width': '33%'})
                        ], style={'display': 'flex'}),
                        
                        html.Button([
                            html.I(className="fas fa-plus"),
                            " Zu Portfolio"
                        ], id={'type': 'add-to-portfolio-btn', 'ticker': stock.get('ticker')},
                           style={
                               'width': '100%',
                               'marginTop': '10px',
                               'backgroundColor': color,
                               'color': 'white',
                               'border': 'none',
                               'padding': '8px',
                               'borderRadius': '4px',
                               'fontSize': '12px'
                           })
                    ])
                ], style={
                    'backgroundColor': 'white',
                    'padding': '15px',
                    'borderRadius': '8px',
                    'border': f'2px solid {color}',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'height': '250px'
                })
                
                cards.append(card)
                
            except Exception as e:
                logger.error(f"Fehler beim Erstellen der Karte für {stock}: {e}")
                continue
        
        return html.Div([
            html.H3("🏆 Top Wachstums-Aktien", style={'marginBottom': '20px'}),
            html.Div(cards, style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(auto-fill, minmax(250px, 1fr))',
                'gap': '15px'
            })
        ])
    
    def _create_no_results_display(self) -> html.Div:
        """Erstelle Anzeige für keine Ergebnisse"""
        return html.Div([
            html.I(className="fas fa-exclamation-circle", 
                  style={'fontSize': '48px', 'color': '#f39c12', 'marginBottom': '10px'}),
            html.H4("Keine Ergebnisse", style={'color': '#f39c12'}),
            html.P("Die Analyse hat keine verwertbaren Ergebnisse geliefert. Versuchen Sie andere Parameter.")
        ], style={
            'textAlign': 'center',
            'backgroundColor': '#fef9e7',
            'padding': '40px',
            'borderRadius': '8px',
            'border': '1px solid #f39c12'
        })
    
    def _create_performance_chart(self, analysis_results: List[Dict]) -> dcc.Graph:
        """
        Erstelle Performance-Chart
        
        Args:
            analysis_results: Analyse-Ergebnisse
            
        Returns:
            dcc.Graph: Performance-Chart
        """
        if not analysis_results:
            return html.Div("Keine Daten für Chart verfügbar")
        
        try:
            # Daten vorbereiten
            tickers = [stock.get('ticker', f'Stock_{i}') for i, stock in enumerate(analysis_results[:10])]
            scores = [float(stock.get('growth_score', 0)) for stock in analysis_results[:10]]
            colors = ['#27ae60' if score >= 80 else '#f39c12' if score >= 60 else '#e74c3c' for score in scores]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=tickers,
                    y=scores,
                    marker_color=colors,
                    text=[f'{score:.1f}' for score in scores],
                    textposition='auto',
                )
            ])
            
            fig.update_layout(
                title='KI-Wachstums-Scores - Top 10 Aktien',
                xaxis_title='Aktien-Ticker',
                yaxis_title='KI-Wachstums-Score',
                template='plotly_white',
                height=400
            )
            
            return dcc.Graph(figure=fig)
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Charts: {e}")
            return html.Div(f"Chart-Fehler: {str(e)}", style={'color': '#e74c3c'})
    
    def setup_callbacks(self):
        """Setup Module-spezifische Callbacks"""
        
        @self.dashboard_app.app.callback(
            [Output('ki-results-container', 'children'),
             Output('ki-charts-container', 'children')],
            [Input('start-analysis-btn', 'n_clicks')],
            [State('market-segment-dropdown', 'value'),
             State('timeframe-dropdown', 'value'),
             State('model-dropdown', 'value')]
        )
        def start_ki_analysis(n_clicks, market_segment, timeframe, model):
            """Starte KI-Analyse"""
            if not n_clicks:
                return self._create_loading_display(), ""
            
            try:
                # API-Call für Analyse
                analysis_request = {
                    "tickers": self._get_tickers_for_segment(market_segment),
                    "timeframe": timeframe,
                    "model_type": model,
                    "analysis_type": "growth_prediction"
                }
                
                response = self.dashboard_app.make_api_call(
                    "/api/analysis/start",
                    "POST",
                    analysis_request
                )
                
                if "error" in response:
                    return html.Div(f"Fehler: {response['error']}", style={'color': '#e74c3c'}), ""
                
                # Ergebnisse verarbeiten
                results_cards = self._create_results_cards(response)
                performance_chart = self._create_performance_chart(response)
                
                return results_cards, performance_chart
                
            except Exception as e:
                logger.error(f"Fehler bei KI-Analyse: {e}")
                return html.Div(f"Analyse-Fehler: {str(e)}", style={'color': '#e74c3c'}), ""
    
    def _get_tickers_for_segment(self, segment: str) -> List[str]:
        """
        Hole Ticker-Liste für Marktsegment
        
        Args:
            segment: Marktsegment (dax, mdax, sdax, all)
            
        Returns:
            List[str]: Ticker-Liste
        """
        # Placeholder - sollte aus Plugin-Datenquellen kommen
        segment_tickers = {
            'dax': ['SAP', 'ASML', 'ADBE', 'MSFT', 'AAPL'],
            'mdax': ['ALV', 'BAS', 'BMW', 'DAI', 'DTE'],
            'sdax': ['ADS', 'BEI', 'CON', 'DB1', 'DPW'],
            'all': ['SAP', 'ASML', 'ADBE', 'MSFT', 'AAPL', 'ALV', 'BAS', 'BMW']
        }
        
        return segment_tickers.get(segment, segment_tickers['dax'])


# Export
__all__ = ['KIWachstumsprognoseModule']