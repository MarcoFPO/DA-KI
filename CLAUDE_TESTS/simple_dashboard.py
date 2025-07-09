#!/usr/bin/env python3
"""
Einfaches Dashboard das GARANTIERT die Buttons zeigt
"""

import dash
from dash import dcc, html, Input, Output, callback
import requests
import json
from datetime import datetime

# Einfache App
app = dash.Dash(__name__)
app.title = "DA-KI - BUTTONS TEST"

# STÄRKSTE NoCache Headers
@app.server.after_request  
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    response.headers['ETag'] = ''
    return response

def hole_wachstumsprognosen():
    """Hole Wachstumsprognosen mit kurzer Timeout"""
    try:
        response = requests.get("http://10.1.1.110:8003/api/wachstumsprognose/top10", timeout=3)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API Fehler: {response.status_code}")
            return {"top_10_wachstums_aktien": []}
    except Exception as e:
        print(f"API Fehler: {e}")
        return {"top_10_wachstums_aktien": []}

# Layout mit GARANTIERT sichtbaren Buttons
app.layout = html.Div([
    html.H1("🚀 DA-KI Dashboard - BUTTONS TEST", 
            style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    html.Div([
        html.H2("📋 Detaillierte Wachstumsprognose mit Firmenprofilen", 
               style={'color': '#e74c3c', 'marginBottom': 20}),
        
        html.Button('🔄 Neu laden', id='refresh-btn',
                   style={'padding': '10px 20px', 'backgroundColor': '#e74c3c', 'color': 'white', 
                          'border': 'none', 'borderRadius': '5px', 'marginBottom': 20}),
        
        html.Div(id='status-div', style={'marginBottom': 20}),
        html.Div(id='tabelle-div')
    ], style={'padding': '20px', 'maxWidth': '1200px', 'margin': '0 auto'}),
    
    # Footer mit eindeutiger Version
    html.Div([
        html.P(f"✅ BUTTONS-TEST-VERSION: {datetime.now().strftime('%H:%M:%S')} | 🎯 Die Buttons MÜSSEN sichtbar sein!",
               style={'textAlign': 'center', 'color': '#27ae60', 'marginTop': 30, 'fontWeight': 'bold'})
    ])
])

@app.callback(
    [Output('tabelle-div', 'children'),
     Output('status-div', 'children')],
    [Input('refresh-btn', 'n_clicks')]
)
def update_tabelle(n_clicks):
    """Erstelle Tabelle mit GARANTIERT sichtbaren Buttons"""
    
    # Hole Daten
    data = hole_wachstumsprognosen()
    aktien = data.get('top_10_wachstums_aktien', [])
    
    # Status
    if not aktien:
        status = html.Div("❌ Keine Daten von API erhalten", 
                         style={'color': 'red', 'padding': '10px', 'backgroundColor': '#f8d7da'})
        
        # Erstelle Dummy-Tabelle mit Buttons als Fallback
        dummy_aktien = [
            {"symbol": "TEST1", "name": "Test Aktie 1", "current_price": 100.0, "wachstums_score": 85},
            {"symbol": "TEST2", "name": "Test Aktie 2", "current_price": 200.0, "wachstums_score": 90}
        ]
        aktien = dummy_aktien
        status = html.Div("⚠️ Zeige Test-Daten mit Buttons", 
                         style={'color': 'orange', 'padding': '10px', 'backgroundColor': '#fff3cd'})
    else:
        status = html.Div(f"✅ {len(aktien)} Aktien geladen", 
                         style={'color': 'green', 'padding': '10px', 'backgroundColor': '#d4edda'})
    
    # Erstelle Tabelle mit GROSSEN sichtbaren Buttons
    zeilen = []
    for i, aktie in enumerate(aktien[:5]):  # Nur die ersten 5 für bessere Performance
        prognose = aktie.get('prognose_30_tage', {})
        score = aktie.get('wachstums_score', 0)
        
        zeile = html.Tr([
            html.Td(f"#{i+1}", style={'fontWeight': 'bold', 'textAlign': 'center', 'padding': '10px'}),
            html.Td([
                html.Strong(aktie['symbol'], style={'fontSize': '16px'}),
                html.Br(),
                html.Small(aktie.get('name', 'N/A')[:30], style={'color': '#7f8c8d'})
            ], style={'padding': '10px'}),
            html.Td(f"€{aktie.get('current_price', 0)}", 
                   style={'fontWeight': 'bold', 'padding': '10px'}),
            html.Td(f"{score:.1f}/100", 
                   style={'fontWeight': 'bold', 'padding': '10px', 'color': '#27ae60'}),
            html.Td(f"€{prognose.get('prognostizierter_preis', 0):.2f}", 
                   style={'fontWeight': 'bold', 'padding': '10px'}),
            html.Td([
                html.Button('📊 ZU LIVE-MONITORING', 
                           id={'type': 'add-to-monitoring-btn', 'index': i},
                           style={
                               'padding': '12px 20px',
                               'backgroundColor': '#e74c3c',
                               'color': 'white',
                               'border': '3px solid #c0392b',
                               'borderRadius': '8px',
                               'fontSize': '14px',
                               'fontWeight': 'bold',
                               'cursor': 'pointer',
                               'boxShadow': '0 4px 8px rgba(0,0,0,0.2)'
                           },
                           title=f"Füge {aktie['symbol']} zu Live-Monitoring hinzu")
            ], style={'padding': '10px', 'textAlign': 'center'})
        ], style={'borderBottom': '2px solid #ecf0f1', 'backgroundColor': '#f8f9fa' if i % 2 == 0 else 'white'})
        
        zeilen.append(zeile)
    
    # Tabelle mit großen Headern
    tabelle = html.Table([
        html.Thead([
            html.Tr([
                html.Th("Rang", style={'padding': '15px', 'backgroundColor': '#e74c3c', 'color': 'white', 'fontWeight': 'bold', 'fontSize': '16px'}),
                html.Th("Aktie", style={'padding': '15px', 'backgroundColor': '#e74c3c', 'color': 'white', 'fontWeight': 'bold', 'fontSize': '16px'}),
                html.Th("Kurs", style={'padding': '15px', 'backgroundColor': '#e74c3c', 'color': 'white', 'fontWeight': 'bold', 'fontSize': '16px'}),
                html.Th("KI-Score", style={'padding': '15px', 'backgroundColor': '#e74c3c', 'color': 'white', 'fontWeight': 'bold', 'fontSize': '16px'}),
                html.Th("Prognose", style={'padding': '15px', 'backgroundColor': '#e74c3c', 'color': 'white', 'fontWeight': 'bold', 'fontSize': '16px'}),
                html.Th("🎯 AKTION", style={'padding': '15px', 'backgroundColor': '#e74c3c', 'color': 'white', 'fontWeight': 'bold', 'fontSize': '16px'})
            ])
        ]),
        html.Tbody(zeilen)
    ], style={
        'width': '100%', 
        'borderCollapse': 'collapse', 
        'backgroundColor': 'white',
        'border': '3px solid #e74c3c',
        'borderRadius': '10px',
        'overflow': 'hidden',
        'boxShadow': '0 4px 8px rgba(0,0,0,0.1)'
    })
    
    return tabelle, status

# Button-Click Handler
@app.callback(
    Output('status-div', 'children', allow_duplicate=True),
    [Input({'type': 'add-to-monitoring-btn', 'index': dash.dependencies.ALL}, 'n_clicks')],
    prevent_initial_call=True
)
def handle_button_click(n_clicks_list):
    if not any(n_clicks_list):
        return dash.no_update
    
    # Finde geklickten Button
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    button_data = json.loads(button_id)
    clicked_index = button_data['index']
    
    # Zeige Erfolg
    return html.Div([
        html.H3("🎉 BUTTON FUNKTIONIERT!", style={'color': '#27ae60', 'margin': 0}),
        html.P(f"Button {clicked_index + 1} wurde geklickt!", style={'margin': '5px 0', 'fontSize': '16px'}),
        html.P("✅ Die Integration zu Live-Monitoring würde jetzt starten", style={'margin': '5px 0'})
    ], style={
        'backgroundColor': '#d4edda',
        'color': '#155724',
        'padding': '20px',
        'borderRadius': '8px',
        'border': '2px solid #c3e6cb',
        'marginBottom': '20px',
        'fontSize': '16px',
        'fontWeight': 'bold'
    })

if __name__ == '__main__':
    print("🚀 Starte EINFACHES Dashboard mit GARANTIERT sichtbaren Buttons...")
    print("📊 URL: http://10.1.1.110:8056")  
    print("🎯 Die Buttons MÜSSEN jetzt sichtbar sein!")
    app.run(debug=True, host='::', port=8056)  # Neuer Port!