#!/usr/bin/env python3
"""
DA-KI Dashboard Enhanced - Mit isolierter Live-Monitoring Integration
Basiert auf dem stabilen dashboard_simple.py + modular Live-Monitoring
"""

import dash
from dash import dcc, html, Input, Output, State, callback, callback_context
import plotly.graph_objs as go
import requests
import json
from datetime import datetime
import time

# Import des isolierten Live-Monitoring Moduls
from live_monitoring_module import (
    create_live_monitoring_instance,
    get_data_interface,
    create_modal_callbacks
)

# App initialisieren
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.title = "🚀 DA-KI Dashboard Enhanced"

# API Konfiguration
API_BASE_URL = "http://10.1.1.110:8003"

# Live-Monitoring Module Instanzen (isoliert)
live_monitoring = create_live_monitoring_instance()
data_interface = get_data_interface()

def hole_aktien_daten():
    """Hole Aktien-Daten von der API mit Fallback (unverändert)"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/wachstumsprognose/top10", timeout=3)
        if response.status_code == 200:
            data = response.json()
            return data.get('top_10_wachstums_aktien', [])
    except:
        pass
    
    # Fallback Mock-Daten (gleich wie vorher)
    return [
        {
            'rank': i+1,
            'symbol': ['SAP.DE', 'ASML.AS', 'SIE.DE', 'NVDA', 'MSFT', 'GOOGL', 'TSLA', 'ADBE', 'CRM', 'ORCL'][i],
            'name': ['SAP SE', 'ASML Holding', 'Siemens AG', 'NVIDIA Corp', 'Microsoft', 'Alphabet', 'Tesla', 'Adobe', 'Salesforce', 'Oracle'][i],
            'branche': ['Software', 'Halbleiter', 'Industrie', 'KI-Chips', 'Software', 'Internet', 'E-Auto', 'Creative', 'CRM', 'Database'][i],
            'wkn': ['716460', 'A0JDGC', '723610', '918422', '870747', 'A14Y6F', 'A1CX3T', '871981', 'A0B4W4', '871460'][i],
            'current_price': [145.50, 742.80, 167.24, 890.45, 425.30, 178.92, 248.50, 485.20, 280.75, 145.80][i],
            'wachstums_score': [95.2, 92.1, 89.7, 88.9, 87.4, 85.7, 84.2, 82.8, 81.6, 80.3][i],
            'prognose_30_tage': {
                'prognostizierter_preis': [158.0, 800.0, 178.5, 950.0, 450.0, 188.0, 265.0, 510.0, 295.0, 152.0][i],
                'erwartete_rendite_prozent': [8.6, 7.7, 6.7, 6.7, 5.8, 5.1, 6.6, 5.1, 5.1, 4.3][i],
                'vertrauen_level': ['Hoch', 'Hoch', 'Mittel', 'Hoch', 'Hoch', 'Mittel', 'Mittel', 'Mittel', 'Mittel', 'Mittel'][i],
                'risiko_level': ['Mittel', 'Mittel', 'Niedrig', 'Hoch', 'Niedrig', 'Mittel', 'Hoch', 'Mittel', 'Mittel', 'Niedrig'][i]
            }
        } for i in range(10)
    ]

def erstelle_karten_layout(aktien_daten):
    """Erstelle 5x2 Karten-Layout (unverändert)"""
    if not aktien_daten:
        return html.Div("Keine Daten verfügbar", style={'textAlign': 'center', 'padding': '40px'})
    
    # Linke Spalte (1-5)
    linke_spalte = []
    for i, aktie in enumerate(aktien_daten[:5]):
        prognose = aktie.get('prognose_30_tage', {})
        karte = html.Div([
            html.H4(f"#{aktie['rank']}", style={'position': 'absolute', 'top': '5px', 'left': '5px', 'color': '#e74c3c'}),
            html.H4(aktie['symbol'], style={'textAlign': 'center', 'marginBottom': 10}),
            html.P(aktie['name'][:25], style={'textAlign': 'center', 'fontSize': '12px', 'color': '#7f8c8d'}),
            html.P(f"🏢 {aktie['branche']}", style={'fontSize': '11px'}),
            html.P(f"🏷️ {aktie['wkn']}", style={'fontSize': '10px', 'color': '#7f8c8d'}),
            html.H3(f"€{aktie['current_price']}", style={'textAlign': 'center', 'color': '#27ae60'}),
            html.P(f"KI-Score: {aktie['wachstums_score']}/100", style={'fontWeight': 'bold', 'color': '#e74c3c'}),
            html.P(f"Rendite: +{prognose.get('erwartete_rendite_prozent', 0):.1f}%", style={'color': '#27ae60'})
        ], style={
            'padding': '15px', 'margin': '10px 0', 'backgroundColor': 'white',
            'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
            'position': 'relative', 'minHeight': '280px'
        })
        linke_spalte.append(karte)
    
    # Rechte Spalte (6-10)
    rechte_spalte = []
    for i, aktie in enumerate(aktien_daten[5:10]):
        prognose = aktie.get('prognose_30_tage', {})
        karte = html.Div([
            html.H4(f"#{aktie['rank']}", style={'position': 'absolute', 'top': '5px', 'left': '5px', 'color': '#e74c3c'}),
            html.H4(aktie['symbol'], style={'textAlign': 'center', 'marginBottom': 10}),
            html.P(aktie['name'][:25], style={'textAlign': 'center', 'fontSize': '12px', 'color': '#7f8c8d'}),
            html.P(f"🏢 {aktie['branche']}", style={'fontSize': '11px'}),
            html.P(f"🏷️ {aktie['wkn']}", style={'fontSize': '10px', 'color': '#7f8c8d'}),
            html.H3(f"€{aktie['current_price']}", style={'textAlign': 'center', 'color': '#27ae60'}),
            html.P(f"KI-Score: {aktie['wachstums_score']}/100", style={'fontWeight': 'bold', 'color': '#e74c3c'}),
            html.P(f"Rendite: +{prognose.get('erwartete_rendite_prozent', 0):.1f}%", style={'color': '#27ae60'})
        ], style={
            'padding': '15px', 'margin': '10px 0', 'backgroundColor': 'white',
            'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
            'position': 'relative', 'minHeight': '280px'
        })
        rechte_spalte.append(karte)
    
    # 5x2 Grid Container
    return html.Div([
        html.Div(linke_spalte, style={'gridColumn': '1'}),
        html.Div(rechte_spalte, style={'gridColumn': '2'})
    ], style={
        'display': 'grid',
        'gridTemplateColumns': '1fr 1fr',
        'gap': '20px',
        'width': '100%'
    })

def erstelle_tabelle_enhanced(aktien_daten):
    """
    ENHANCED: Erstelle Tabelle mit Live-Monitoring Integration
    Verwendet isolierte Live-Monitoring Module
    """
    if not aktien_daten:
        return html.P("Keine Daten verfügbar")
    
    zeilen = []
    for i, aktie in enumerate(aktien_daten):
        prognose = aktie.get('prognose_30_tage', {})
        
        # Normale Tabellenzellen
        normale_zellen = [
            html.Td(f"#{aktie['rank']}", style={'fontWeight': 'bold'}),
            html.Td(aktie['symbol']),
            html.Td(aktie['branche']),
            html.Td(aktie['wkn']),
            html.Td(f"€{aktie['current_price']}"),
            html.Td(f"{aktie['wachstums_score']}/100"),
            html.Td(f"€{prognose.get('prognostizierter_preis', 0):.2f}"),
            html.Td(f"+{prognose.get('erwartete_rendite_prozent', 0):.1f}%", style={'color': '#27ae60'}),
            html.Td(prognose.get('vertrauen_level', 'N/A'))
        ]
        
        # NEUE: Action-Spalte vom Live-Monitoring Module
        action_cell = live_monitoring.create_action_column_button(aktie, i)
        normale_zellen.append(action_cell)
        
        zeile = html.Tr(normale_zellen)
        zeilen.append(zeile)
    
    return html.Table([
        html.Thead([
            html.Tr([
                html.Th("Rang", style={'padding': '10px', 'backgroundColor': '#e74c3c', 'color': 'white'}),
                html.Th("Aktie", style={'padding': '10px', 'backgroundColor': '#e74c3c', 'color': 'white'}),
                html.Th("Branche", style={'padding': '10px', 'backgroundColor': '#e74c3c', 'color': 'white'}),
                html.Th("WKN", style={'padding': '10px', 'backgroundColor': '#e74c3c', 'color': 'white'}),
                html.Th("Kurs", style={'padding': '10px', 'backgroundColor': '#e74c3c', 'color': 'white'}),
                html.Th("KI-Score", style={'padding': '10px', 'backgroundColor': '#e74c3c', 'color': 'white'}),
                html.Th("30T Prognose", style={'padding': '10px', 'backgroundColor': '#e74c3c', 'color': 'white'}),
                html.Th("Rendite", style={'padding': '10px', 'backgroundColor': '#e74c3c', 'color': 'white'}),
                html.Th("Vertrauen", style={'padding': '10px', 'backgroundColor': '#e74c3c', 'color': 'white'}),
                html.Th("🎯 Aktion", style={'padding': '10px', 'backgroundColor': '#e74c3c', 'color': 'white'})  # NEUE SPALTE
            ])
        ]),
        html.Tbody(zeilen)
    ], style={'width': '100%', 'borderCollapse': 'collapse'})

def erstelle_charts(aktien_daten):
    """Erstelle Charts für Ranking und Rendite (unverändert)"""
    if not aktien_daten:
        empty_chart = {
            'data': [],
            'layout': {'title': 'Keine Daten verfügbar', 'height': 300}
        }
        return empty_chart, empty_chart
    
    # Ranking Chart
    symbols = [aktie['symbol'] for aktie in aktien_daten]
    scores = [aktie['wachstums_score'] for aktie in aktien_daten]
    
    ranking_chart = {
        'data': [go.Bar(x=symbols, y=scores, marker_color='#e74c3c')],
        'layout': go.Layout(
            title='KI-Wachstums-Score TOP 10',
            xaxis={'title': 'Aktien'},
            yaxis={'title': 'Score'},
            height=300
        )
    }
    
    # Rendite Chart
    renditen = [aktie.get('prognose_30_tage', {}).get('erwartete_rendite_prozent', 0) for aktie in aktien_daten]
    
    rendite_chart = {
        'data': [go.Bar(x=symbols, y=renditen, marker_color='#27ae60')],
        'layout': go.Layout(
            title='30-Tage Rendite-Prognose',
            xaxis={'title': 'Aktien'},
            yaxis={'title': 'Rendite (%)'},
            height=300
        )
    }
    
    return ranking_chart, rendite_chart

def update_portfolio_summary():
    """Helper: Aktualisiere Portfolio-Zusammenfassung"""
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

def update_portfolio_positions():
    """Helper: Aktualisiere Portfolio-Positionen Tabelle"""
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
    
    return html.Table([
        html.Thead([
            html.Tr([
                html.Th("Symbol", style={'padding': '8px', 'backgroundColor': '#3498db', 'color': 'white'}),
                html.Th("Name", style={'padding': '8px', 'backgroundColor': '#3498db', 'color': 'white'}),
                html.Th("Anzahl", style={'padding': '8px', 'backgroundColor': '#3498db', 'color': 'white'}),
                html.Th("Kurs", style={'padding': '8px', 'backgroundColor': '#3498db', 'color': 'white'}),
                html.Th("Investiert", style={'padding': '8px', 'backgroundColor': '#3498db', 'color': 'white'}),
                html.Th("Wert", style={'padding': '8px', 'backgroundColor': '#3498db', 'color': 'white'}),
                html.Th("Gewinn/Verlust", style={'padding': '8px', 'backgroundColor': '#3498db', 'color': 'white'}),
                html.Th("Hinzugefügt", style={'padding': '8px', 'backgroundColor': '#3498db', 'color': 'white'}),
                html.Th("Aktion", style={'padding': '8px', 'backgroundColor': '#3498db', 'color': 'white'})
            ])
        ]),
        html.Tbody(zeilen)
    ], style={'width': '100%', 'borderCollapse': 'collapse', 'backgroundColor': 'white'})

# Statische Daten beim Start laden
AKTIEN_DATEN = hole_aktien_daten()

# ENHANCED Layout mit Live-Monitoring
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("🚀 DA-KI Dashboard Enhanced", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 10}),
        html.P("Mit Live-Monitoring Integration • Stabile und modular aufgebaute Version", 
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
    
    # KI-Wachstumsprognose Karten (5x2 Layout)
    html.Div([
        html.H2("📈 KI-Wachstumsprognose (5x2 Layout)", 
               style={'color': '#e74c3c', 'marginBottom': 20}),
        html.Div(id='aktien-karten', children=erstelle_karten_layout(AKTIEN_DATEN))
    ], style={'backgroundColor': '#fff5f5', 'padding': '20px', 'marginBottom': '20px', 
              'borderRadius': '10px', 'border': '2px solid #e74c3c'}),
    
    # Charts
    html.Div([
        html.Div([
            html.H3("📊 Wachstums-Score", style={'textAlign': 'center'}),
            dcc.Graph(id='ranking-chart')
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            html.H3("📈 Rendite-Prognose", style={'textAlign': 'center'}),
            dcc.Graph(id='rendite-chart')
        ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%'})
    ], style={'marginBottom': 20}),
    
    # ENHANCED: Tabelle mit Live-Monitoring Buttons
    html.Div([
        html.H3("📋 Detaillierte Prognose-Tabelle mit Live-Monitoring Integration", 
               style={'color': '#2c3e50'}),
        html.Div(id='prognose-tabelle', children=erstelle_tabelle_enhanced(AKTIEN_DATEN))
    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': 20}),
    
    # NEUE: Live-Monitoring Dashboard (vom isolierten Modul)
    html.Div(id='live-monitoring-dashboard', children=live_monitoring.create_live_monitoring_dashboard()),
    
    # NEUE: Modal Dialog (vom isolierten Modul)
    live_monitoring.create_modal_dialog(),
    
    # Footer
    html.Div([
        html.P(f"🤖 Enhanced DA-KI Dashboard mit Live-Monitoring | 🕒 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",
               style={'textAlign': 'center', 'color': '#95a5a6', 'marginTop': 30})
    ])
], style={'margin': '20px'})

# ================== CALLBACKS ==================

# Basis-Callback für Dashboard-Refresh (unverändert)
@app.callback(
    [Output('aktien-karten', 'children'),
     Output('ranking-chart', 'figure'),
     Output('rendite-chart', 'figure'),
     Output('prognose-tabelle', 'children'),
     Output('status-message', 'children')],
    [Input('refresh-btn', 'n_clicks')]
)
def update_dashboard(n_clicks):
    """Basis Dashboard Update (unverändert)"""
    try:
        aktien_daten = hole_aktien_daten()
        
        karten = erstelle_karten_layout(aktien_daten)
        ranking_chart, rendite_chart = erstelle_charts(aktien_daten)
        tabelle = erstelle_tabelle_enhanced(aktien_daten)  # ENHANCED Version
        
        status = html.Div([
            html.Span(f"✅ {len(aktien_daten)} Aktien geladen | Letztes Update: {datetime.now().strftime('%H:%M:%S')}", 
                     style={'color': '#27ae60', 'fontWeight': 'bold'})
        ], style={'padding': '10px', 'backgroundColor': '#d4edda', 'borderRadius': '5px'})
        
        return karten, ranking_chart, rendite_chart, tabelle, status
        
    except Exception as e:
        error_msg = html.Div([
            html.Span(f"⚠️ Fehler beim Laden der Daten: {str(e)}", 
                     style={'color': '#e74c3c', 'fontWeight': 'bold'})
        ], style={'padding': '10px', 'backgroundColor': '#f8d7da', 'borderRadius': '5px'})
        
        karten = erstelle_karten_layout(AKTIEN_DATEN)
        ranking_chart, rendite_chart = erstelle_charts(AKTIEN_DATEN)
        tabelle = erstelle_tabelle_enhanced(AKTIEN_DATEN)
        
        return karten, ranking_chart, rendite_chart, tabelle, error_msg

# NEUE: Live-Monitoring Modal Callback
@app.callback(
    [Output('live-monitoring-modal', 'style'),
     Output('selected-stock-info', 'children'),
     Output('position-shares-input', 'value'),
     Output('position-investment-input', 'value')],
    [Input({'type': 'add-to-monitoring-btn', 'index': 'ALL'}, 'n_clicks')],
    prevent_initial_call=True
)
def show_position_modal(n_clicks_list):
    """Zeige Modal für Position-Hinzufügung"""
    if not any(n_clicks_list):
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # Finde geklickten Button
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    try:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        button_data = json.loads(button_id)
        clicked_index = button_data['index']
        
        # Hole Aktien-Daten über Interface
        aktien_daten = hole_aktien_daten()
        aktie_data = data_interface.extract_aktie_data(aktien_daten, clicked_index)
        
        if aktie_data:
            stock_info = data_interface.format_stock_info_for_modal(aktie_data)
            
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
        print(f"Modal-Fehler: {e}")
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

# NEUE: Position-Management Callback
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
def handle_portfolio_actions(confirm_clicks, cancel_clicks, clear_clicks, remove_clicks, 
                           stock_info, shares, investment):
    """Handle Portfolio-Aktionen über isoliertes Modul"""
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, ""
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    modal_style = {'display': 'none'}
    message = ""
    
    try:
        if button_id == 'cancel-add-position-btn':
            # Einfach Modal schließen
            pass
            
        elif button_id == 'confirm-add-position-btn' and confirm_clicks:
            # Position hinzufügen über isoliertes Modul
            aktien_daten = hole_aktien_daten()
            
            # Versuche Symbol aus stock_info zu extrahieren
            symbol = "UNKNOWN"
            if stock_info and hasattr(stock_info, 'children') and len(stock_info['children']) > 0:
                symbol = stock_info['children'][0]['props']['children']
            
            # Finde passende Aktie
            aktie_data = None
            for aktie in aktien_daten:
                if aktie['symbol'] == symbol:
                    aktie_data = aktie
                    break
            
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
            # Alle Positionen löschen
            result = live_monitoring.clear_all_positions()
            message = html.Div([
                html.Span(f"🗑️ {result['message']}", style={'color': '#e74c3c', 'fontWeight': 'bold'})
            ], style={'padding': '10px', 'backgroundColor': '#f8d7da', 'borderRadius': '5px'})
            
        elif 'remove-position-btn' in button_id:
            # Einzelne Position entfernen
            button_data = json.loads(button_id)
            position_id = button_data['index']
            result = live_monitoring.remove_position(position_id)
            message = html.Div([
                html.Span(f"🗑️ {result['message']}", style={'color': '#e74c3c', 'fontWeight': 'bold'})
            ], style={'padding': '10px', 'backgroundColor': '#f8d7da', 'borderRadius': '5px'})
    
    except Exception as e:
        message = html.Div([
            html.Span(f"❌ Fehler: {str(e)}", style={'color': '#e74c3c', 'fontWeight': 'bold'})
        ], style={'padding': '10px', 'backgroundColor': '#f8d7da', 'borderRadius': '5px'})
    
    # Portfolio-Daten aktualisieren
    portfolio_summary = update_portfolio_summary()
    portfolio_positions = update_portfolio_positions()
    
    return modal_style, portfolio_summary, portfolio_positions, message

if __name__ == '__main__':
    print("🚀 Starte Enhanced DA-KI Dashboard...")
    print("📊 URL: http://10.1.1.110:8057")
    print("✨ Mit isolierter Live-Monitoring Integration!")
    print("🔗 Modulare Architektur mit definierten Schnittstellen")
    app.run(debug=False, host='0.0.0.0', port=8057)