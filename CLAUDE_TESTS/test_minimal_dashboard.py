#!/usr/bin/env python3
"""
Minimaler Dashboard-Test nur für Button
"""

import sys
sys.path.append('/home/mdoehler/data-web-app/frontend')

from dash import Dash, html, Input, Output
import requests

app = Dash(__name__)

# Minimales Layout mit Button und Progress
app.layout = html.Div([
    html.H1("🔄 Minimaler Button-Test"),
    html.Button("🔄 Prognose neu berechnen", id='refresh-btn', 
                style={'padding': '10px 20px', 'backgroundColor': '#3498db', 'color': 'white', 
                       'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer'}),
    html.Div([
        html.Div(id='progress-bar', style={
            'width': '0%', 'height': '20px', 'backgroundColor': '#27ae60', 
            'borderRadius': '10px', 'transition': 'width 0.3s ease'
        })
    ], id='progress-container', style={
        'width': '300px', 'height': '20px', 'backgroundColor': '#ecf0f1',
        'borderRadius': '10px', 'overflow': 'hidden', 'margin': '20px', 'display': 'none'
    }),
    html.Div(id='progress-text', style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '20px'}),
    html.Div(id='status-message', style={'margin': '20px'})
])

@app.callback(
    [Output('status-message', 'children'),
     Output('progress-container', 'style'),
     Output('progress-bar', 'style'),
     Output('progress-text', 'children'),
     Output('refresh-btn', 'disabled')],
    [Input('refresh-btn', 'n_clicks')]
)
def update_button(n_clicks):
    print(f"🔧 MINIMAL TEST: Button geklickt! n_clicks = {n_clicks}")
    
    if not n_clicks:
        return (
            "Bereit für Test",
            {'display': 'none'},
            {'width': '0%', 'height': '20px', 'backgroundColor': '#27ae60', 'borderRadius': '10px'},
            "",
            False
        )
    
    # Button-Klick verarbeiten
    try:
        print("🔄 Rufe API auf...")
        response = requests.post("http://10.1.1.110:8003/api/wachstumsprognose/berechnen", timeout=5)
        
        if response.status_code == 200:
            print("✅ API-Call erfolgreich!")
            return (
                "✅ Prognose-Neuberechnung gestartet!",
                {'width': '300px', 'height': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px', 'overflow': 'hidden', 'margin': '20px', 'display': 'block'},
                {'width': '100%', 'height': '20px', 'backgroundColor': '#27ae60', 'borderRadius': '10px', 'transition': 'width 0.3s ease'},
                "✅ API-Call erfolgreich!",
                False
            )
        else:
            print(f"❌ API-Fehler: {response.status_code}")
            return (
                f"❌ API-Fehler: {response.status_code}",
                {'display': 'none'},
                {'width': '0%', 'height': '20px', 'backgroundColor': '#e74c3c', 'borderRadius': '10px'},
                f"❌ API-Fehler: {response.status_code}",
                False
            )
    except Exception as e:
        print(f"⚠️ Verbindungsfehler: {e}")
        return (
            f"⚠️ Verbindungsfehler: {str(e)}",
            {'display': 'none'},
            {'width': '0%', 'height': '20px', 'backgroundColor': '#f39c12', 'borderRadius': '10px'},
            f"⚠️ Verbindungsfehler: {str(e)}",
            False
        )

if __name__ == '__main__':
    print("🧪 Starte minimalen Dashboard-Test...")
    print("📊 URL: http://10.1.1.110:8057")
    app.run(debug=True, host='0.0.0.0', port=8057)