#!/usr/bin/env python3
"""
Einfacher Button-Test mit Fortschrittsbalken
"""

from dash import Dash, html, dcc, Input, Output, callback
import requests

app = Dash(__name__)

app.layout = html.Div([
    html.H1("🔄 Button-Test"),
    html.Button("🔄 Prognose neu berechnen", id='test-refresh-btn', 
                style={'padding': '10px 20px', 'backgroundColor': '#3498db', 'color': 'white', 
                       'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer'}),
    html.Div([
        html.Div(id='test-progress-bar', style={
            'width': '0%', 'height': '20px', 'backgroundColor': '#27ae60', 
            'borderRadius': '10px', 'transition': 'width 0.3s ease'
        })
    ], id='test-progress-container', style={
        'width': '300px', 'height': '20px', 'backgroundColor': '#ecf0f1',
        'borderRadius': '10px', 'overflow': 'hidden', 'margin': '20px', 'display': 'none'
    }),
    html.Div(id='test-progress-text', style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '20px'}),
    html.Div(id='test-status', style={'margin': '20px'})
])

@app.callback(
    [Output('test-progress-container', 'style'),
     Output('test-progress-bar', 'style'),
     Output('test-progress-text', 'children'),
     Output('test-status', 'children'),
     Output('test-refresh-btn', 'disabled')],
    [Input('test-refresh-btn', 'n_clicks')]
)
def test_button_function(n_clicks):
    if not n_clicks:
        return (
            {'display': 'none'},
            {'width': '0%', 'height': '20px', 'backgroundColor': '#27ae60', 'borderRadius': '10px'},
            "",
            "Bereit für Test",
            False
        )
    
    # Button wurde geklickt
    progress_container_style = {
        'width': '300px', 'height': '20px', 'backgroundColor': '#ecf0f1',
        'borderRadius': '10px', 'overflow': 'hidden', 'margin': '20px', 'display': 'block'
    }
    
    # Test API-Call
    try:
        response = requests.post("http://10.1.1.110:8003/api/wachstumsprognose/berechnen", timeout=5)
        if response.status_code == 200:
            progress_bar_style = {
                'width': '100%', 'height': '20px', 'backgroundColor': '#27ae60',
                'borderRadius': '10px', 'transition': 'width 0.3s ease'
            }
            progress_text = "✅ API-Call erfolgreich!"
            status = "✅ Prognose-Neuberechnung gestartet!"
            button_disabled = False
        else:
            progress_bar_style = {
                'width': '50%', 'height': '20px', 'backgroundColor': '#e74c3c',
                'borderRadius': '10px', 'transition': 'width 0.3s ease'
            }
            progress_text = f"❌ API-Fehler: {response.status_code}"
            status = f"❌ API-Fehler: {response.status_code}"
            button_disabled = False
    except Exception as e:
        progress_bar_style = {
            'width': '30%', 'height': '20px', 'backgroundColor': '#f39c12',
            'borderRadius': '10px', 'transition': 'width 0.3s ease'
        }
        progress_text = f"⚠️ Verbindungsfehler: {str(e)}"
        status = f"⚠️ Verbindungsfehler: {str(e)}"
        button_disabled = False
    
    return (progress_container_style, progress_bar_style, progress_text, status, button_disabled)

if __name__ == '__main__':
    print("🧪 Starte einfachen Button-Test...")
    print("📊 URL: http://10.1.1.110:8056")
    app.run(debug=False, host='0.0.0.0', port=8056)