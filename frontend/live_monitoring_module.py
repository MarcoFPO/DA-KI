#!/usr/bin/env python3
"""
Live-Monitoring Module - Isolierte Komponente für Portfolio-Management
Definierte Schnittstellen für Datenaustausch mit dem Hauptdashboard
"""

from dash import html, dcc, Input, Output, State, callback_context
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class LiveMonitoringModule:
    """Isolierte Live-Monitoring Komponente mit definierten Schnittstellen"""
    
    def __init__(self):
        self.portfolio_positions = []  # Interne Datenhaltung
        self.position_counter = 0
        
    # ================== PUBLIC INTERFACES ==================
    
    def create_action_column_button(self, aktie_data: Dict, index: int) -> html.Td:
        """
        SCHNITTSTELLE: Erstelle Action-Button für Tabellenspalte
        
        Input: aktie_data (Dict) - Einzelne Aktie mit allen Daten
        Output: html.Td - Fertige Tabellenzelle mit Button
        """
        button = html.Button(
            '📊 Zu Live-Monitoring',
            id={'type': 'add-to-monitoring-btn', 'index': index},
            style={
                'padding': '8px 12px',
                'backgroundColor': '#3498db',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'fontSize': '10px',
                'cursor': 'pointer',
                'width': '100%'
            }
        )
        
        return html.Td(button, style={'textAlign': 'center', 'padding': '5px'})
    
    def create_modal_dialog(self) -> html.Div:
        """
        SCHNITTSTELLE: Erstelle Modal-Dialog für Positionsauswahl
        
        Output: html.Div - Vollständiger Modal-Dialog
        """
        return html.Div(
            id='live-monitoring-modal',
            children=[
                html.Div([
                    html.H3("📊 Position zum Live-Monitoring hinzufügen", 
                           style={'color': '#2c3e50', 'marginBottom': 20}),
                    
                    # Aktien-Info Container
                    html.Div(id='selected-stock-info', style={'marginBottom': 20}),
                    
                    # Anzahl Aktien Input
                    html.Label("🔢 Anzahl Aktien:", style={'fontWeight': 'bold', 'marginBottom': 10}),
                    dcc.Input(
                        id='position-shares-input',
                        type='number',
                        value=10,
                        min=1,
                        max=1000,
                        style={'width': '100%', 'padding': '10px', 'marginBottom': 15}
                    ),
                    
                    # Investment Input
                    html.Label("💶 Investment (EUR):", style={'fontWeight': 'bold', 'marginBottom': 10}),
                    dcc.Input(
                        id='position-investment-input',
                        type='number',
                        value=1000,
                        min=100,
                        max=100000,
                        step=100,
                        style={'width': '100%', 'padding': '10px', 'marginBottom': 20}
                    ),
                    
                    # Action Buttons
                    html.Div([
                        html.Button(
                            '✅ Position hinzufügen',
                            id='confirm-add-position-btn',
                            style={
                                'padding': '10px 20px',
                                'backgroundColor': '#27ae60',
                                'color': 'white',
                                'border': 'none',
                                'borderRadius': '5px',
                                'marginRight': 10,
                                'cursor': 'pointer'
                            }
                        ),
                        html.Button(
                            '❌ Abbrechen',
                            id='cancel-add-position-btn',
                            style={
                                'padding': '10px 20px',
                                'backgroundColor': '#e74c3c',
                                'color': 'white',
                                'border': 'none',
                                'borderRadius': '5px',
                                'cursor': 'pointer'
                            }
                        )
                    ], style={'textAlign': 'center'})
                    
                ], style={
                    'backgroundColor': 'white',
                    'padding': '30px',
                    'borderRadius': '10px',
                    'boxShadow': '0 4px 20px rgba(0,0,0,0.3)',
                    'width': '500px',
                    'margin': '0 auto',
                    'marginTop': '50px'
                })
            ],
            style={
                'display': 'none',
                'position': 'fixed',
                'top': 0,
                'left': 0,
                'width': '100%',
                'height': '100%',
                'backgroundColor': 'rgba(0,0,0,0.5)',
                'zIndex': 1000
            }
        )
    
    def create_live_monitoring_dashboard(self) -> html.Div:
        """
        SCHNITTSTELLE: Erstelle Live-Monitoring Dashboard Bereich
        
        Output: html.Div - Vollständiger Live-Monitoring Bereich
        """
        return html.Div([
            html.H2("📊 Live-Monitoring Dashboard", 
                   style={'color': '#3498db', 'marginBottom': 20}),
            
            # Portfolio Summary Cards
            html.Div(id='portfolio-summary-cards', children=self._create_empty_summary()),
            
            # Portfolio Positions Table
            html.Div([
                html.H3("📋 Aktuelle Positionen", style={'color': '#2c3e50', 'marginBottom': 15}),
                html.Div(id='portfolio-positions-table', children=self._create_empty_positions_table())
            ], style={'marginTop': 20}),
            
            # Portfolio Management Actions
            html.Div([
                html.Button(
                    '🗑️ Alle Positionen löschen',
                    id='clear-all-positions-btn',
                    style={
                        'padding': '10px 20px',
                        'backgroundColor': '#e74c3c',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '5px',
                        'marginTop': 20,
                        'cursor': 'pointer'
                    }
                )
            ])
            
        ], style={
            'backgroundColor': '#f0f8ff',
            'padding': '20px',
            'marginBottom': '20px',
            'borderRadius': '10px',
            'border': '2px solid #3498db'
        })
    
    def add_position(self, aktie_data: Dict, shares: int, investment: float) -> Dict[str, Any]:
        """
        SCHNITTSTELLE: Füge neue Position zum Portfolio hinzu
        
        Input: 
            - aktie_data (Dict): Aktien-Informationen
            - shares (int): Anzahl Aktien
            - investment (float): Investment-Betrag
            
        Output: Dict mit Status und Ergebnis
        """
        try:
            # Prüfe Portfolio-Limit (max 10 Positionen)
            if len(self.portfolio_positions) >= 10:
                return {
                    'success': False,
                    'message': 'Portfolio ist voll (max. 10 Positionen)',
                    'position_count': len(self.portfolio_positions)
                }
            
            # Prüfe auf Duplikate
            for position in self.portfolio_positions:
                if position['symbol'] == aktie_data['symbol']:
                    return {
                        'success': False,
                        'message': f'{aktie_data["symbol"]} bereits im Portfolio',
                        'position_count': len(self.portfolio_positions)
                    }
            
            # Erstelle neue Position
            new_position = {
                'id': f'pos_{self.position_counter}',
                'symbol': aktie_data['symbol'],
                'name': aktie_data.get('name', 'N/A'),
                'shares': shares,
                'investment': investment,
                'current_price': aktie_data.get('current_price', 0),
                'added_date': datetime.now().strftime('%d.%m.%Y %H:%M'),
                'wachstums_score': aktie_data.get('wachstums_score', 0)
            }
            
            self.portfolio_positions.append(new_position)
            self.position_counter += 1
            
            return {
                'success': True,
                'message': f'{aktie_data["symbol"]} erfolgreich hinzugefügt',
                'position_count': len(self.portfolio_positions),
                'position': new_position
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Fehler beim Hinzufügen: {str(e)}',
                'position_count': len(self.portfolio_positions)
            }
    
    def remove_position(self, position_id: str) -> Dict[str, Any]:
        """
        SCHNITTSTELLE: Entferne Position aus Portfolio
        
        Input: position_id (str) - ID der zu entfernenden Position
        Output: Dict mit Status und Ergebnis
        """
        try:
            for i, position in enumerate(self.portfolio_positions):
                if position['id'] == position_id:
                    removed_position = self.portfolio_positions.pop(i)
                    return {
                        'success': True,
                        'message': f'{removed_position["symbol"]} entfernt',
                        'position_count': len(self.portfolio_positions)
                    }
            
            return {
                'success': False,
                'message': 'Position nicht gefunden',
                'position_count': len(self.portfolio_positions)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Fehler beim Entfernen: {str(e)}',
                'position_count': len(self.portfolio_positions)
            }
    
    def clear_all_positions(self) -> Dict[str, Any]:
        """
        SCHNITTSTELLE: Lösche alle Positionen
        
        Output: Dict mit Status
        """
        position_count = len(self.portfolio_positions)
        self.portfolio_positions = []
        
        return {
            'success': True,
            'message': f'{position_count} Positionen gelöscht',
            'position_count': 0
        }
    
    def get_portfolio_data(self) -> Dict[str, Any]:
        """
        SCHNITTSTELLE: Hole vollständige Portfolio-Daten
        
        Output: Dict mit Portfolio-Zusammenfassung
        """
        if not self.portfolio_positions:
            return {
                'position_count': 0,
                'total_investment': 0,
                'total_value': 0,
                'avg_score': 0,
                'positions': []
            }
        
        total_investment = sum(pos['investment'] for pos in self.portfolio_positions)
        total_value = sum(pos['shares'] * pos['current_price'] for pos in self.portfolio_positions)
        avg_score = sum(pos['wachstums_score'] for pos in self.portfolio_positions) / len(self.portfolio_positions)
        
        return {
            'position_count': len(self.portfolio_positions),
            'total_investment': total_investment,
            'total_value': total_value,
            'avg_score': avg_score,
            'positions': self.portfolio_positions.copy()
        }
    
    # ================== PRIVATE HELPERS ==================
    
    def _create_empty_summary(self) -> html.Div:
        """Private: Erstelle leere Portfolio-Zusammenfassung"""
        return html.Div([
            html.Div([
                html.H4("0", style={'margin': 0, 'color': '#3498db'}),
                html.P("Positionen", style={'margin': 0, 'fontSize': '12px'})
            ], style={
                'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#ebf3fd',
                'borderRadius': '10px', 'width': '22%', 'display': 'inline-block', 'margin': '1%'
            }),
            
            html.Div([
                html.H4("€0", style={'margin': 0, 'color': '#27ae60'}),
                html.P("Investiert", style={'margin': 0, 'fontSize': '12px'})
            ], style={
                'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#eafaf1',
                'borderRadius': '10px', 'width': '22%', 'display': 'inline-block', 'margin': '1%'
            }),
            
            html.Div([
                html.H4("€0", style={'margin': 0, 'color': '#f39c12'}),
                html.P("Aktueller Wert", style={'margin': 0, 'fontSize': '12px'})
            ], style={
                'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#fef9e7',
                'borderRadius': '10px', 'width': '22%', 'display': 'inline-block', 'margin': '1%'
            }),
            
            html.Div([
                html.H4("0/100", style={'margin': 0, 'color': '#e74c3c'}),
                html.P("Ø KI-Score", style={'margin': 0, 'fontSize': '12px'})
            ], style={
                'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#fdf2f2',
                'borderRadius': '10px', 'width': '22%', 'display': 'inline-block', 'margin': '1%'
            })
        ])
    
    def _create_empty_positions_table(self) -> html.Div:
        """Private: Erstelle leere Positionen-Tabelle"""
        return html.Div([
            html.P("📭 Keine Positionen im Portfolio", 
                  style={
                      'textAlign': 'center', 
                      'color': '#7f8c8d', 
                      'fontSize': '16px',
                      'padding': '40px'
                  })
        ], style={
            'backgroundColor': 'white',
            'borderRadius': '10px',
            'border': '1px solid #ecf0f1'
        })

# ================== DATENINTERFACE ==================

class MonitoringDataInterface:
    """Definierte Schnittstelle für Datenaustausch zwischen Modulen"""
    
    @staticmethod
    def extract_aktie_data(aktien_list: List[Dict], index: int) -> Optional[Dict]:
        """
        Extrahiere Aktien-Daten für spezifischen Index
        
        Input: aktien_list, index
        Output: Aktien-Daten oder None
        """
        try:
            if 0 <= index < len(aktien_list):
                return aktien_list[index]
            return None
        except:
            return None
    
    @staticmethod
    def format_stock_info_for_modal(aktie_data: Dict) -> html.Div:
        """
        Formatiere Aktien-Info für Modal-Anzeige
        
        Input: aktie_data
        Output: Formatierte HTML-Darstellung
        """
        if not aktie_data:
            return html.Div("Fehler: Keine Aktien-Daten")
        
        return html.Div([
            html.H4(f"{aktie_data.get('symbol', 'N/A')}", 
                   style={'color': '#2c3e50', 'margin': '0'}),
            html.P(f"{aktie_data.get('name', 'N/A')}", 
                  style={'color': '#7f8c8d', 'fontSize': '14px', 'margin': '5px 0'}),
            html.P(f"Aktueller Kurs: €{aktie_data.get('current_price', 0)}", 
                  style={'fontWeight': 'bold', 'color': '#27ae60', 'margin': '5px 0'}),
            html.P(f"KI-Score: {aktie_data.get('wachstums_score', 0)}/100", 
                  style={'color': '#e74c3c', 'margin': '5px 0'})
        ], style={
            'padding': '15px',
            'backgroundColor': '#f8f9fa',
            'borderRadius': '5px',
            'border': '1px solid #dee2e6'
        })

# ================== EXPORT ==================

def create_live_monitoring_instance():
    """Factory-Funktion für Module-Instanz"""
    return LiveMonitoringModule()

def get_data_interface():
    """Factory-Funktion für Daten-Interface"""
    return MonitoringDataInterface()

# ================== CALLBACK HELPERS ==================

def create_modal_callbacks():
    """
    Definiere Callback-Pattern für Modal-Interaktionen
    Wird vom Hauptdashboard verwendet
    """
    return {
        'show_modal_inputs': [Input({'type': 'add-to-monitoring-btn', 'index': 'ALL'}, 'n_clicks')],
        'show_modal_outputs': [
            Output('live-monitoring-modal', 'style'),
            Output('selected-stock-info', 'children'),
            Output('position-shares-input', 'value'),
            Output('position-investment-input', 'value')
        ],
        'confirm_modal_inputs': [
            Input('confirm-add-position-btn', 'n_clicks'),
            Input('cancel-add-position-btn', 'n_clicks')
        ],
        'confirm_modal_states': [
            State('selected-stock-info', 'children'),
            State('position-shares-input', 'value'),
            State('position-investment-input', 'value')
        ],
        'confirm_modal_outputs': [
            Output('live-monitoring-modal', 'style', allow_duplicate=True),
            Output('portfolio-summary-cards', 'children'),
            Output('portfolio-positions-table', 'children')
        ]
    }