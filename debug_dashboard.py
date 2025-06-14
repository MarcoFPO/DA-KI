#!/usr/bin/env python3
"""
Debug Version des Dashboards nur für die Tabelle mit Buttons
"""

import dash
from dash import dcc, html, Input, Output, callback
import requests
import json
from datetime import datetime

# Einfache App
app = dash.Dash(__name__)
app.title = "DA-KI Debug - Live-Monitoring Buttons"

# NoCache Headers
@app.server.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

def hole_wachstumsprognosen():
    """Hole Top 10 Wachstumsprognosen"""
    try:
        response = requests.get("http://localhost:8003/api/wachstumsprognose/top10", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"top_10_wachstums_aktien": [], "cache_status": "error"}
    except Exception as e:
        print(f"Fehler bei Wachstumsprognose: {e}")
        return {"top_10_wachstums_aktien": [], "cache_status": "error"}

# Einfaches Layout nur für die Tabelle
app.layout = html.Div([
    html.H1("🚀 DA-KI Debug - Live-Monitoring Integration", 
            style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    html.Div([
        html.H2("📋 Detaillierte Wachstumsprognose mit Live-Monitoring Buttons", 
               style={'color': '#e74c3c', 'marginBottom': 20}),
        
        html.Button('🔄 Daten neu laden', id='refresh-btn',
                   style={'padding': '10px 20px', 'backgroundColor': '#e74c3c', 'color': 'white', 
                          'border': 'none', 'borderRadius': '5px', 'marginBottom': 20}),
        
        html.Div(id='status-anzeige', style={'marginBottom': 20}),
        html.Div(id='tabelle-container')
    ], style={'padding': '20px', 'maxWidth': '1200px', 'margin': '0 auto'})
])

@app.callback(
    [Output('tabelle-container', 'children'),
     Output('status-anzeige', 'children')],
    [Input('refresh-btn', 'n_clicks')]
)
def update_tabelle(n_clicks):
    # Hole Wachstumsprognosen
    prognose_data = hole_wachstumsprognosen()
    top_10 = prognose_data.get('top_10_wachstums_aktien', [])
    
    # Status
    if not top_10:
        status = html.Div("❌ Keine Wachstumsprognosen verfügbar", 
                         style={'color': 'red', 'padding': '10px', 'backgroundColor': '#f8d7da', 'borderRadius': '5px'})
        return html.P("Keine Daten verfügbar"), status
    
    status = html.Div(f"✅ {len(top_10)} Wachstumsprognosen geladen", 
                     style={'color': 'green', 'padding': '10px', 'backgroundColor': '#d4edda', 'borderRadius': '5px'})
    
    # Erstelle Tabelle mit Buttons
    tabelle_zeilen = []
    for i, aktie in enumerate(top_10):
        prognose = aktie.get('prognose_30_tage', {})
        score = aktie.get('wachstums_score', 0)
        
        # Button Style
        button_style = {
            'padding': '8px 12px',
            'backgroundColor': '#3498db',
            'color': 'white',
            'border': 'none',
            'borderRadius': '5px',
            'fontSize': '12px',
            'cursor': 'pointer',
            'fontWeight': 'bold'
        }
        
        zeile = html.Tr([
            html.Td(f"#{i+1}", style={'fontWeight': 'bold', 'textAlign': 'center', 'padding': '10px'}),
            html.Td([
                html.Strong(aktie['symbol'], style={'fontSize': '14px'}),
                html.Br(),
                html.Small(aktie.get('name', 'N/A')[:25], style={'color': '#7f8c8d'})
            ], style={'padding': '10px'}),
            html.Td(f"€{aktie.get('current_price', 0)}", 
                   style={'fontWeight': 'bold', 'padding': '10px'}),
            html.Td(f"{score:.1f}/100", 
                   style={'fontWeight': 'bold', 'padding': '10px', 'color': '#27ae60' if score >= 80 else '#f39c12' if score >= 70 else '#e74c3c'}),
            html.Td(f"€{prognose.get('prognostizierter_preis', 0):.2f}", 
                   style={'fontWeight': 'bold', 'padding': '10px'}),
            html.Td([
                html.Button('📊 Zu Live-Monitoring', 
                           id={'type': 'add-to-monitoring-btn', 'index': i},
                           style=button_style,
                           title=f"{aktie['symbol']} zu Live-Monitoring hinzufügen")
            ], style={'padding': '10px', 'textAlign': 'center'})
        ], style={'borderBottom': '1px solid #ecf0f1'})
        
        tabelle_zeilen.append(zeile)
    
    # Tabelle
    tabelle = html.Table([
        html.Thead([
            html.Tr([
                html.Th("Rang", style={'padding': '12px', 'backgroundColor': '#e74c3c', 'color': 'white', 'fontWeight': 'bold'}),
                html.Th("Aktie", style={'padding': '12px', 'backgroundColor': '#e74c3c', 'color': 'white', 'fontWeight': 'bold'}),
                html.Th("Kurs", style={'padding': '12px', 'backgroundColor': '#e74c3c', 'color': 'white', 'fontWeight': 'bold'}),
                html.Th("KI-Score", style={'padding': '12px', 'backgroundColor': '#e74c3c', 'color': 'white', 'fontWeight': 'bold'}),
                html.Th("30T Prognose", style={'padding': '12px', 'backgroundColor': '#e74c3c', 'color': 'white', 'fontWeight': 'bold'}),
                html.Th("Aktion", style={'padding': '12px', 'backgroundColor': '#e74c3c', 'color': 'white', 'fontWeight': 'bold'})
            ])
        ]),
        html.Tbody(tabelle_zeilen)
    ], style={
        'width': '100%', 
        'borderCollapse': 'collapse', 
        'backgroundColor': 'white',
        'border': '1px solid #ddd',
        'borderRadius': '8px',
        'overflow': 'hidden',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
    })
    
    return tabelle, status

# Callback für Button-Clicks
@app.callback(
    Output('status-anzeige', 'children', allow_duplicate=True),
    [Input({'type': 'add-to-monitoring-btn', 'index': dash.dependencies.ALL}, 'n_clicks')],
    prevent_initial_call=True
)
def handle_button_click(n_clicks_list):
    if not any(n_clicks_list):
        return dash.no_update
    
    # Finde welcher Button geklickt wurde
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    import json
    button_data = json.loads(button_id)
    clicked_index = button_data['index']
    
    # Hole aktuelle Wachstumsprognosen um Symbol zu finden
    prognose_data = hole_wachstumsprognosen()
    top_10 = prognose_data.get('top_10_wachstums_aktien', [])
    
    if clicked_index < len(top_10):
        selected_stock = top_10[clicked_index]
        symbol = selected_stock['symbol']
        name = selected_stock.get('name', 'N/A')
        
        # Zeige Bestätigungsmeldung
        return html.Div([
            html.H4(f"✅ Button geklickt!", style={'color': '#27ae60', 'margin': 0}),
            html.P(f"Aktie: {symbol} ({name})", style={'margin': '5px 0'}),
            html.P(f"Index: {clicked_index}", style={'margin': '5px 0'}),
            html.P("Die Position-Auswahl würde sich jetzt öffnen.", style={'margin': '5px 0'})
        ], style={
            'backgroundColor': '#d4edda',
            'color': '#155724',
            'padding': '15px',
            'borderRadius': '5px',
            'border': '1px solid #c3e6cb',
            'marginBottom': '20px'
        })
    
    return html.Div("❌ Fehler beim Button-Click", style={'color': 'red'})

if __name__ == '__main__':
    print("🔧 Starte Debug Dashboard auf Port 8055...")
    print("📊 URL: http://localhost:8055")
    print("🎯 Teste die Live-Monitoring Buttons!")
    app.run(debug=True, host='0.0.0.0', port=8055)