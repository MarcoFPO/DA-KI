#!/usr/bin/env python3
"""
DA-KI Dashboard Modular - Vollständig modulare Architektur
Alle Teilprojekte als isolierte Module mit definierten Schnittstellen
"""

import dash
from dash import dcc, html, Input, Output, State, callback, callback_context
import json
from datetime import datetime

# Import aller isolierten Module
from live_monitoring_module import (
    create_live_monitoring_instance,
    get_data_interface as get_live_monitoring_interface,
)
from ki_wachstumsprognose_module import (
    create_wachstumsprognose_instance,
    get_wachstumsprognose_data_interface
)

# App initialisieren
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.title = "🚀 DA-KI Dashboard"

# ================== MODULARE INSTANZEN ==================

# Alle Module isoliert instanziieren
live_monitoring = create_live_monitoring_instance()
live_monitoring_interface = get_live_monitoring_interface()
wachstumsprognose = create_wachstumsprognose_instance()
wachstums_interface = get_wachstumsprognose_data_interface()

# Statische Daten beim Start laden (über Module)
AKTIEN_DATEN = wachstumsprognose.get_aktien_daten()

# ================== MODULAR ENHANCED FUNCTIONS ==================

def erstelle_enhanced_tabelle_mit_live_monitoring(aktien_daten):
    """
    Erstelle Enhanced Tabelle durch Kombination beider Module
    Basis-Tabelle vom Wachstumsprognose-Modul + Action-Spalte vom Live-Monitoring
    """
    if not aktien_daten:
        return html.P("Keine Daten verfügbar")
    
    # Hole Basis-Tabelle vom Wachstumsprognose-Modul
    basis_tabelle = wachstumsprognose.create_prognose_tabelle_basis(aktien_daten)
    
    # Erstelle erweiterte Tabelle mit Action-Spalte
    zeilen = []
    for i, aktie in enumerate(aktien_daten):
        prognose = aktie.get('prognose_30_tage', {})
        
        # Basis-Zellen (vom Wachstumsprognose-Modul Schema)
        basis_zellen = [
            html.Td(f"#{aktie['rank']}", style={'fontWeight': 'bold'}),
            html.Td(aktie['symbol']),
            html.Td(aktie['branche']),
            html.Td(aktie['wkn']),
            html.Td(f"€{aktie['current_price']}"),
            html.Td(f"{aktie['wachstums_score']}/100"),
            html.Td(f"€{prognose.get('prognostizierter_preis', 0):.2f}"),
            html.Td(f"+{prognose.get('erwartete_rendite_prozent', 0):.1f}%", 
                    style={'color': '#27ae60'}),
            html.Td(prognose.get('vertrauen_level', 'N/A'))
        ]
        
        # Action-Spalte vom Live-Monitoring Modul
        action_cell = live_monitoring.create_action_column_button(aktie, i)
        basis_zellen.append(action_cell)
        
        zeile = html.Tr(basis_zellen)
        zeilen.append(zeile)
    
    # Erweiterte Header-Definition
    header_style = {'padding': '10px', 'backgroundColor': '#e74c3c', 'color': 'white'}
    
    return html.Table([
        html.Thead([
            html.Tr([
                html.Th("Rang", style=header_style),
                html.Th("Aktie", style=header_style),
                html.Th("Branche", style=header_style),
                html.Th("WKN", style=header_style),
                html.Th("Kurs", style=header_style),
                html.Th("KI-Score", style=header_style),
                html.Th("30T Prognose", style=header_style),
                html.Th("Rendite", style=header_style),
                html.Th("Vertrauen", style=header_style),
                html.Th("🎯 Aktion", style=header_style)  # Action-Spalte für Live-Monitoring
            ])
        ]),
        html.Tbody(zeilen)
    ], style={'width': '100%', 'borderCollapse': 'collapse'})

def erstelle_status_info_modular(aktien_daten):
    """Erstelle Status-Info durch Kombination beider Module"""
    # Wachstumsprognose Status
    wachstums_status = wachstumsprognose.get_status_info(aktien_daten)
    
    # Live-Monitoring Status
    portfolio_data = live_monitoring.get_portfolio_data()
    
    # Portfolio Metriken
    portfolio_metriken = wachstums_interface.calculate_portfolio_metrics(aktien_daten)
    
    return {
        'wachstumsprognose': wachstums_status,
        'live_monitoring': {
            'portfolio_count': portfolio_data['position_count'],
            'portfolio_value': portfolio_data['total_value']
        },
        'combined_metrics': portfolio_metriken
    }

def update_portfolio_summary_modular():
    """Portfolio-Zusammenfassung Update über Live-Monitoring Modul"""
    portfolio_data = live_monitoring.get_portfolio_data()
    
    if portfolio_data['position_count'] == 0:
        return live_monitoring._create_empty_summary()
    
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

def update_portfolio_positions_modular():
    """Portfolio-Positionen Update über Live-Monitoring Modul"""
    portfolio_data = live_monitoring.get_portfolio_data()
    
    if portfolio_data['position_count'] == 0:
        return live_monitoring._create_empty_positions_table()
    
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

# Enhanced Tabelle mit Action-Buttons nach Funktions-Definition erstellen
ENHANCED_TABELLE_MIT_BUTTONS = erstelle_enhanced_tabelle_mit_live_monitoring(AKTIEN_DATEN)

# ================== MODULAR LAYOUT ==================

app.layout = html.Div([
    # Header
    html.Div([
        html.H1("🚀 DA-KI Dashboard", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 10}),
        html.P("Modulare Architektur • KI-Wachstumsprognose mit Live-Monitoring", 
               style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': 30})
    ]),
    
    # Refresh Button
    html.Div([
        html.Button('🔄 Daten aktualisieren', id='refresh-btn', 
                   style={'padding': '10px 20px', 'backgroundColor': '#3498db', 'color': 'white',
                          'border': 'none', 'borderRadius': '5px', 'marginBottom': 20})
    ]),
    
    # Status & Action Messages
    html.Div(id='status-message', style={'marginBottom': 20}),
    html.Div(id='action-message', style={'marginBottom': 20}),
    
    # MODUL 1: KI-Wachstumsprognose (isoliert)
    html.Div(id='wachstumsprognose-container', 
             children=wachstumsprognose.create_wachstumsprognose_container(AKTIEN_DATEN)),
    
    # MODUL 2: Charts Container (isoliert)
    html.Div(id='charts-container', 
             children=wachstumsprognose.create_charts_container(AKTIEN_DATEN)),
    
    # MODUL 3: Enhanced Tabelle (Kombination beider Module)
    html.Div([
        html.H3("📋 Detaillierte Wachstumsprognose mit Firmenprofilen", 
               style={'color': '#2c3e50'}),
        html.Div(id='prognose-tabelle', children=ENHANCED_TABELLE_MIT_BUTTONS)
    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': 20}),
    
    # MODUL 4: Live-Monitoring Dashboard (isoliert)
    html.Div(id='live-monitoring-dashboard', children=live_monitoring.create_live_monitoring_dashboard()),
    
    # MODUL 5: Modal Dialog (isoliert)
    live_monitoring.create_modal_dialog(),
    
    # Footer
    html.Div([
        html.P(f"🤖 Modular DA-KI Dashboard | 🕒 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')} | 🔧 Alle Module isoliert",
               style={'textAlign': 'center', 'color': '#95a5a6', 'marginTop': 30})
    ])
], style={'margin': '20px'})

# ================== MODULAR CALLBACKS ==================

# Haupt-Dashboard Callback (modular)
@app.callback(
    [Output('wachstumsprognose-container', 'children'),
     Output('charts-container', 'children'),
     Output('prognose-tabelle', 'children'),
     Output('status-message', 'children')],
    [Input('refresh-btn', 'n_clicks')]
)
def update_dashboard_vollstaendig_modular(n_clicks):
    """Vollständig modularer Dashboard-Update"""
    try:
        # Hole Daten über Wachstumsprognose-Modul
        aktien_daten = wachstumsprognose.get_aktien_daten()
        
        # Erstelle Komponenten über isolierte Module
        wachstums_container = wachstumsprognose.create_wachstumsprognose_container(aktien_daten)
        charts_container = wachstumsprognose.create_charts_container(aktien_daten)
        enhanced_tabelle = erstelle_enhanced_tabelle_mit_live_monitoring(aktien_daten)
        
        # Status über kombinierte Module-Interfaces
        status_info = erstelle_status_info_modular(aktien_daten)
        
        status = html.Div([
            html.Span(f"✅ {status_info['wachstumsprognose']['anzahl_aktien']} Aktien | "
                     f"Update: {status_info['wachstumsprognose']['letztes_update']} | "
                     f"Quelle: {status_info['wachstumsprognose']['data_source']} | "
                     f"Ø Score: {status_info['wachstumsprognose']['avg_score']:.1f} | "
                     f"Portfolio: {status_info['live_monitoring']['portfolio_count']} Positionen", 
                     style={'color': '#27ae60', 'fontWeight': 'bold'})
        ], style={'padding': '10px', 'backgroundColor': '#d4edda', 'borderRadius': '5px'})
        
        return wachstums_container, charts_container, enhanced_tabelle, status
        
    except Exception as e:
        error_msg = html.Div([
            html.Span(f"⚠️ Fehler beim modularen Update: {str(e)}", 
                     style={'color': '#e74c3c', 'fontWeight': 'bold'})
        ], style={'padding': '10px', 'backgroundColor': '#f8d7da', 'borderRadius': '5px'})
        
        # Fallback über Module
        fallback_data = wachstumsprognose.get_aktien_daten()
        wachstums_container = wachstumsprognose.create_wachstumsprognose_container(fallback_data)
        charts_container = wachstumsprognose.create_charts_container(fallback_data)
        enhanced_tabelle = erstelle_enhanced_tabelle_mit_live_monitoring(fallback_data)
        
        return wachstums_container, charts_container, enhanced_tabelle, error_msg

# Live-Monitoring Modal Callback (isoliert)
@app.callback(
    [Output('live-monitoring-modal', 'style'),
     Output('selected-stock-info', 'children'),
     Output('position-shares-input', 'value'),
     Output('position-investment-input', 'value')],
    [Input({'type': 'add-to-monitoring-btn', 'index': 'ALL'}, 'n_clicks')],
    prevent_initial_call=True
)
def show_position_modal_modular(n_clicks_list):
    """Modal-Anzeige über isolierte Module"""
    if not any(n_clicks_list):
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    try:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        button_data = json.loads(button_id)
        clicked_index = button_data['index']
        
        # Hole Daten über Wachstumsprognose-Modul
        aktien_daten = wachstumsprognose.get_aktien_daten()
        aktie_data = live_monitoring_interface.extract_aktie_data(aktien_daten, clicked_index)
        
        if aktie_data:
            stock_info = live_monitoring_interface.format_stock_info_for_modal(aktie_data)
            
            # Berechne Standard-Werte
            default_shares = max(1, int(1000 / aktie_data.get('current_price', 100)))
            default_investment = default_shares * aktie_data.get('current_price', 100)
            
            # Modal anzeigen
            modal_style = {
                'display': 'block',
                'position': 'fixed',
                'top': 0,
                'left': 0,
                'width': '100%',
                'height': '100%',
                'backgroundColor': 'rgba(0,0,0,0.5)',
                'zIndex': 1000
            }
            
            return modal_style, stock_info, default_shares, default_investment
        
    except Exception as e:
        print(f"Modal-Fehler (modular): {e}")
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

# Portfolio-Management Callback (isoliert)
@app.callback(
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
def handle_portfolio_actions_modular(confirm_clicks, cancel_clicks, clear_clicks, remove_clicks, 
                                   stock_info, shares, investment):
    """Portfolio-Aktionen über isolierte Live-Monitoring Module"""
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, ""
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    modal_style = {'display': 'none'}
    message = ""
    
    try:
        if button_id == 'cancel-add-position-btn':
            pass
            
        elif button_id == 'confirm-add-position-btn' and confirm_clicks:
            # Hole Daten über Wachstumsprognose-Modul
            aktien_daten = wachstumsprognose.get_aktien_daten()
            
            # Extrahiere Symbol aus stock_info
            symbol = "UNKNOWN"
            if stock_info and hasattr(stock_info, 'children') and len(stock_info['children']) > 0:
                symbol = stock_info['children'][0]['props']['children']
            
            # Finde Aktie über Wachstums-Interface
            aktie_data = wachstums_interface.extract_aktie_by_symbol(aktien_daten, symbol)
            
            if aktie_data and shares and investment:
                result = live_monitoring.add_position(aktie_data, int(shares), float(investment))
                
                if result['success']:
                    message = html.Div([
                        html.Span(f"✅ {result['message']}", style={'color': '#27ae60', 'fontWeight': 'bold'})
                    ], style={'padding': '10px', 'backgroundColor': '#d4edda', 'borderRadius': '5px'})
                else:
                    message = html.Div([
                        html.Span(f"⚠️ {result['message']}", style={'color': '#f39c12', 'fontWeight': 'bold'})
                    ], style={'padding': '10px', 'backgroundColor': '#fff3cd', 'borderRadius': '5px'})
            
        elif button_id == 'clear-all-positions-btn' and clear_clicks:
            result = live_monitoring.clear_all_positions()
            message = html.Div([
                html.Span(f"🗑️ {result['message']}", style={'color': '#e74c3c', 'fontWeight': 'bold'})
            ], style={'padding': '10px', 'backgroundColor': '#f8d7da', 'borderRadius': '5px'})
            
        elif 'remove-position-btn' in button_id:
            button_data = json.loads(button_id)
            position_id = button_data['index']
            result = live_monitoring.remove_position(position_id)
            message = html.Div([
                html.Span(f"🗑️ {result['message']}", style={'color': '#e74c3c', 'fontWeight': 'bold'})
            ], style={'padding': '10px', 'backgroundColor': '#f8d7da', 'borderRadius': '5px'})
    
    except Exception as e:
        message = html.Div([
            html.Span(f"❌ Modular-Fehler: {str(e)}", style={'color': '#e74c3c', 'fontWeight': 'bold'})
        ], style={'padding': '10px', 'backgroundColor': '#f8d7da', 'borderRadius': '5px'})
    
    # Portfolio-Updates über modulare Funktionen
    portfolio_summary = update_portfolio_summary_modular()
    portfolio_positions = update_portfolio_positions_modular()
    
    return modal_style, portfolio_summary, portfolio_positions, message

if __name__ == '__main__':
    print("🚀 Starte DA-KI Dashboard (Modulare Architektur)...")
    print("📊 URL: http://10.1.1.110:8054")
    print("🔧 Modulare Teilprojekte:")
    print("   - KI-Wachstumsprognose Module")
    print("   - Live-Monitoring Module") 
    print("   - Definierte Schnittstellen für Datenaustausch")
    print("⚠️  VERBOTEN: Verwendung von Loopback-Adressen (127.0.0.1, localhost)")
    print("⚠️  NUR IP 10.1.1.110 und Port 8054 verwenden!")
    app.run(debug=False, host='0.0.0.0', port=8054)