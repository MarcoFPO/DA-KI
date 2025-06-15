#!/usr/bin/env python3
"""
Frontend Callback Module - Isolierte Callback-Verwaltung
Definierte Schnittstellen für Callback-Management und Event-Handling
"""

import dash
from dash import Input, Output, State, callback, callback_context
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable

class FrontendCallbackModule:
    """Isoliertes Frontend-Callback-Modul mit Event-Management"""
    
    def __init__(self, app: dash.Dash):
        self.app = app
        self.callback_registry = {}
        self.event_handlers = {}
        
    # ================== PUBLIC CALLBACK INTERFACES ==================
    
    def register_dashboard_update_callback(self, orchestrator, components: Dict[str, str]):
        """
        SCHNITTSTELLE: Registriere Haupt-Dashboard Update Callback
        
        Input:
            orchestrator - Dashboard-Orchestrator Instanz
            components (Dict[str, str]) - Mapping von Component-IDs zu Update-Methoden
        """
        @self.app.callback(
            [Output(comp_id, 'children') for comp_id in components.keys()] + 
            [Output('status-message', 'children')],
            [Input('refresh-btn', 'n_clicks')]
        )
        def update_dashboard_orchestrated(n_clicks):
            """Orchestrierter Dashboard-Update über Module"""
            try:
                # Daten über Wachstumsprognose-Modul laden
                aktien_daten = orchestrator.wachstumsprognose.get_aktien_daten()
                
                # Validierung über Tabelle-Interface
                validation = orchestrator.tabelle_interface.validate_aktien_data_structure(aktien_daten)
                if not validation['valid']:
                    error_msg = orchestrator.layout_interface.format_status_message(
                        f"Daten-Validierung fehlgeschlagen: {validation['error']}", 
                        "error"
                    )
                    fallback_outputs = [dash.no_update] * len(components)
                    return fallback_outputs + [error_msg]
                
                # Komponenten über Module erstellen
                component_outputs = []
                for comp_id, update_method in components.items():
                    if hasattr(orchestrator, update_method):
                        component = getattr(orchestrator, update_method)(aktien_daten)
                        component_outputs.append(component)
                    else:
                        component_outputs.append(dash.no_update)
                
                # Status-Nachricht über Layout-Interface
                stats = orchestrator.tabelle_interface.get_table_summary_stats(aktien_daten)
                status_msg = (f"✅ {stats['count']} Aktien geladen | "
                            f"Ø Score: {stats['avg_score']:.1f} | "
                            f"Top: {stats['top_performer']} | "
                            f"Update: {datetime.now().strftime('%H:%M:%S')}")
                
                status = orchestrator.layout_interface.format_status_message(status_msg, "success")
                
                return component_outputs + [status]
                
            except Exception as e:
                error_msg = orchestrator.layout_interface.format_status_message(
                    f"Fehler beim Dashboard-Update: {str(e)}", 
                    "error"
                )
                
                # Fallback-Outputs
                fallback_outputs = [dash.no_update] * len(components)
                return fallback_outputs + [error_msg]
        
        self.callback_registry['dashboard_update'] = update_dashboard_orchestrated
    
    def register_modal_callback(self, orchestrator):
        """
        SCHNITTSTELLE: Registriere Modal-Dialog Callback
        
        Input: orchestrator - Dashboard-Orchestrator Instanz
        """
        @self.app.callback(
            [Output('live-monitoring-modal', 'style'),
             Output('selected-stock-info', 'children'),
             Output('position-shares-input', 'value'),
             Output('position-investment-input', 'value')],
            [Input({'type': 'add-to-monitoring-btn', 'index': 'ALL'}, 'n_clicks')],
            prevent_initial_call=True
        )
        def show_modal_callback_orchestrated(n_clicks_list):
            """Modal-Anzeige über orchestrierte Module"""
            if not any(n_clicks_list):
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update
            
            ctx = callback_context
            if not ctx.triggered:
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update
            
            try:
                # Event-Daten extrahieren
                event_data = self._extract_callback_event_data(ctx)
                if not event_data:
                    return dash.no_update, dash.no_update, dash.no_update, dash.no_update
                
                clicked_index = event_data['index']
                
                # Daten über Wachstumsprognose-Modul
                aktien_daten = orchestrator.wachstumsprognose.get_aktien_daten()
                aktie_data = orchestrator.live_monitoring_interface.extract_aktie_data(aktien_daten, clicked_index)
                
                if aktie_data:
                    stock_info = orchestrator.live_monitoring_interface.format_stock_info_for_modal(aktie_data)
                    
                    # Standard-Werte berechnen
                    default_shares = max(1, int(1000 / aktie_data.get('current_price', 100)))
                    default_investment = default_shares * aktie_data.get('current_price', 100)
                    
                    # Modal-Style
                    modal_style = self._create_modal_style()
                    
                    return modal_style, stock_info, default_shares, default_investment
                
            except Exception as e:
                print(f"Modal-Fehler (Callback-Modul): {e}")
            
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        self.callback_registry['modal_show'] = show_modal_callback_orchestrated
    
    def register_portfolio_callback(self, orchestrator):
        """
        SCHNITTSTELLE: Registriere Portfolio-Management Callback
        
        Input: orchestrator - Dashboard-Orchestrator Instanz  
        """
        @self.app.callback(
            [Output('live-monitoring-modal', 'style', allow_duplicate=True),
             Output('portfolio-summary-cards', 'children'),
             Output('portfolio-positions-table', 'children'),
             Output('action-message', 'children')],
            [Input('confirm-add-position-btn', 'n_clicks'),
             Input('cancel-add-position-btn', 'n_clicks'),
             Input('clear-all-positions-btn', 'n_clicks'),
             Input({'type': 'remove-position-btn', 'index': 'ALL'}, 'n_clicks')],
            [State('selected-stock-info', 'children'),
             State('position-shares-input', 'value'),
             State('position-investment-input', 'value')],
            prevent_initial_call=True
        )
        def handle_portfolio_callback_orchestrated(confirm_clicks, cancel_clicks, clear_clicks, remove_clicks, 
                                        stock_info, shares, investment):
            """Portfolio-Management über orchestrierte Module"""
            ctx = callback_context
            if not ctx.triggered:
                return dash.no_update, dash.no_update, dash.no_update, ""
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            modal_style = {'display': 'none'}
            message = ""
            
            try:
                # Portfolio-Aktionen verarbeiten
                action_result = self._process_portfolio_action(
                    button_id, orchestrator, stock_info, shares, investment,
                    confirm_clicks, clear_clicks
                )
                
                if action_result:
                    message = orchestrator.layout_interface.format_status_message(
                        action_result['message'], 
                        action_result['type']
                    )
            
            except Exception as e:
                message = orchestrator.layout_interface.format_status_message(
                    f"❌ Callback-Fehler: {str(e)}", 
                    "error"
                )
            
            # Portfolio-Updates über Orchestrator
            portfolio_data = orchestrator.live_monitoring.get_portfolio_data()
            
            if portfolio_data['position_count'] == 0:
                portfolio_summary = orchestrator.live_monitoring._create_empty_summary()
                portfolio_positions = orchestrator.live_monitoring._create_empty_positions_table()
            else:
                portfolio_summary = orchestrator._update_portfolio_summary(portfolio_data)
                portfolio_positions = orchestrator._update_portfolio_positions(portfolio_data)
            
            return modal_style, portfolio_summary, portfolio_positions, message
        
        self.callback_registry['portfolio_management'] = handle_portfolio_callback_orchestrated
    
    def setup_all_callbacks(self, orchestrator):
        """
        SCHNITTSTELLE: Setup aller Callbacks für Orchestrator
        
        Input: orchestrator - Dashboard-Orchestrator Instanz
        """
        # Dashboard-Update Callback
        components_mapping = {
            'wachstumsprognose-container': '_create_wachstumsprognose_section',
            'charts-container': '_create_charts_section', 
            'prognose-tabelle-section': '_create_enhanced_tabelle_section'
        }
        self.register_dashboard_update_callback(orchestrator, components_mapping)
        
        # Modal und Portfolio Callbacks
        self.register_modal_callback(orchestrator)
        self.register_portfolio_callback(orchestrator)
    
    # ================== PRIVATE HELPER METHODS ==================
    
    def _extract_callback_event_data(self, ctx) -> Optional[Dict]:
        """Private: Extrahiere Event-Daten aus Callback-Context"""
        try:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            button_data = json.loads(button_id)
            return button_data
        except (json.JSONDecodeError, KeyError, IndexError):
            return None
    
    def _create_modal_style(self) -> Dict[str, Any]:
        """Private: Erstelle Modal-Style-Definition"""
        return {
            'display': 'block',
            'position': 'fixed',
            'top': 0,
            'left': 0,
            'width': '100%',
            'height': '100%',
            'backgroundColor': 'rgba(0,0,0,0.5)',
            'zIndex': 1000
        }
    
    def _process_portfolio_action(self, button_id: str, orchestrator, stock_info, shares, investment,
                                confirm_clicks, clear_clicks) -> Optional[Dict[str, str]]:
        """Private: Verarbeite Portfolio-Aktionen"""
        if button_id == 'cancel-add-position-btn':
            return None
            
        elif button_id == 'confirm-add-position-btn' and confirm_clicks:
            # Daten über Wachstumsprognose-Modul
            aktien_daten = orchestrator.wachstumsprognose.get_aktien_daten()
            
            # Symbol extrahieren
            symbol = "UNKNOWN"
            if stock_info and hasattr(stock_info, 'children') and len(stock_info['children']) > 0:
                symbol = stock_info['children'][0]['props']['children']
            
            # Aktie über Wachstums-Interface finden
            aktie_data = orchestrator.wachstums_interface.extract_aktie_by_symbol(aktien_daten, symbol)
            
            if aktie_data and shares and investment:
                result = orchestrator.live_monitoring.add_position(aktie_data, int(shares), float(investment))
                
                return {
                    'message': f"✅ {result['message']}" if result['success'] else f"⚠️ {result['message']}",
                    'type': 'success' if result['success'] else 'warning'
                }
        
        elif button_id == 'clear-all-positions-btn' and clear_clicks:
            result = orchestrator.live_monitoring.clear_all_positions()
            return {
                'message': f"🗑️ {result['message']}",
                'type': 'info'
            }
            
        elif 'remove-position-btn' in button_id:
            button_data = json.loads(button_id)
            position_id = button_data['index']
            result = orchestrator.live_monitoring.remove_position(position_id)
            return {
                'message': f"🗑️ {result['message']}",
                'type': 'info'
            }
        
        return None
    
    # ================== INTERFACE QUERIES ==================
    
    def get_registered_callbacks(self) -> List[str]:
        """
        SCHNITTSTELLE: Hole Liste registrierter Callbacks
        
        Output: List[str] - Liste der Callback-Namen
        """
        return list(self.callback_registry.keys())
    
    def get_callback_statistics(self) -> Dict[str, Any]:
        """
        SCHNITTSTELLE: Hole Callback-Statistiken
        
        Output: Dict mit Callback-Statistiken
        """
        return {
            'total_callbacks': len(self.callback_registry),
            'callback_names': list(self.callback_registry.keys()),
            'setup_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'module_status': 'active'
        }

# ================== EXPORT ==================

def create_frontend_callback_instance(app: dash.Dash):
    """Factory-Funktion für Frontend-Callback-Instanz"""
    return FrontendCallbackModule(app)

def get_callback_interface():
    """Factory-Funktion für Callback-Interface"""
    return FrontendCallbackModule