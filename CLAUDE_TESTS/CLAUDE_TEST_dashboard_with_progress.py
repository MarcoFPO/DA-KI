#!/usr/bin/env python3
"""
CLAUDE_TEST: Dashboard mit expliziter Fortschrittsbalken-Darstellung
⚠️ TESTCODE - ZEIGT WIE FORTSCHRITTSBALKEN AUSSEHEN SOLLTEN
"""

import dash
from dash import dcc, html, Input, Output
import requests

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("🔄 CLAUDE_TEST: Fortschrittsbalken-Demo"),
    
    html.Div([
        html.Button('🔄 Prognose neu berechnen', 
                   id='refresh-growth-btn', 
                   style={
                       'padding': '10px 20px', 
                       'backgroundColor': '#e74c3c', 
                       'color': 'white',
                       'border': 'none', 
                       'borderRadius': '5px', 
                       'marginBottom': '15px',
                       'fontSize': '14px',
                       'cursor': 'pointer'
                   }),
        
        # FORTSCHRITTSBALKEN - SO SOLLTE ES AUSSEHEN
        html.Div([
            html.Div(id='progress-bar-real', style={
                'width': '0%', 
                'height': '25px', 
                'backgroundColor': '#27ae60', 
                'borderRadius': '12px', 
                'transition': 'width 0.5s ease',
                'position': 'relative',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center'
            })
        ], id='progress-container-real', style={
            'width': '400px', 
            'height': '25px', 
            'backgroundColor': '#ecf0f1',
            'borderRadius': '12px', 
            'overflow': 'hidden', 
            'margin': '15px 0',
            'border': '2px solid #bdc3c7',
            'display': 'none'  # Initial versteckt
        }),
        
        html.Div(id='progress-text-real', 
                style={
                    'fontSize': '14px', 
                    'color': '#2c3e50', 
                    'margin': '10px 0',
                    'fontWeight': 'bold',
                    'textAlign': 'center'
                }),
        
        html.Div(id='status-area', 
                style={
                    'margin': '20px 0',
                    'padding': '15px',
                    'backgroundColor': '#f8f9fa',
                    'borderRadius': '8px',
                    'border': '1px solid #dee2e6'
                })
    ], style={
        'maxWidth': '600px',
        'margin': '50px auto',
        'padding': '30px',
        'backgroundColor': 'white',
        'borderRadius': '15px',
        'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
        'textAlign': 'center'
    })
])

@app.callback(
    [Output('progress-container-real', 'style'),
     Output('progress-bar-real', 'style'),
     Output('progress-text-real', 'children'),
     Output('status-area', 'children'),
     Output('refresh-growth-btn', 'disabled')],
    [Input('refresh-growth-btn', 'n_clicks')]
)
def update_progress(n_clicks):
    import time
    
    if not n_clicks:
        return (
            {'display': 'none'},
            {'width': '0%', 'height': '25px', 'backgroundColor': '#27ae60', 'borderRadius': '12px'},
            "",
            "Bereit für Test - Klicken Sie den Button!",
            False
        )
    
    # Simuliere Progress-Bar Schritte
    progress_phases = [
        (20, "🔄 Starte Neuberechnung...", "#3498db"),
        (40, "📊 Verbinde mit Backend...", "#f39c12"), 
        (60, "🤖 KI berechnet Prognosen...", "#9b59b6"),
        (80, "📈 Aktualisiere Daten...", "#e67e22"),
        (100, "✅ Abgeschlossen!", "#27ae60")
    ]
    
    # Nimm den aktuellen Schritt basierend auf n_clicks
    phase_index = min(n_clicks - 1, len(progress_phases) - 1)
    width, text, color = progress_phases[phase_index]
    
    if width < 100:
        # Laufend
        progress_container_style = {
            'width': '400px', 
            'height': '25px', 
            'backgroundColor': '#ecf0f1',
            'borderRadius': '12px', 
            'overflow': 'hidden', 
            'margin': '15px 0',
            'border': '2px solid #bdc3c7',
            'display': 'block'
        }
        
        progress_bar_style = {
            'width': f'{width}%',
            'height': '25px',
            'backgroundColor': color,
            'borderRadius': '12px',
            'transition': 'width 0.5s ease, background-color 0.3s ease',
            'position': 'relative',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center'
        }
        
        status = f"🔄 Progress: {width}% - {text}"
        button_disabled = True
        
    else:
        # Abgeschlossen
        progress_container_style = {
            'width': '400px', 
            'height': '25px', 
            'backgroundColor': '#d4edda',
            'borderRadius': '12px', 
            'overflow': 'hidden', 
            'margin': '15px 0',
            'border': '2px solid #27ae60',
            'display': 'block'
        }
        
        progress_bar_style = {
            'width': '100%',
            'height': '25px',
            'backgroundColor': '#27ae60',
            'borderRadius': '12px',
            'transition': 'width 0.5s ease',
            'position': 'relative',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center'
        }
        
        status = "✅ Prognose-Neuberechnung erfolgreich abgeschlossen!"
        button_disabled = False
    
    # Test Backend-API
    try:
        api_response = requests.post("http://10.1.1.110:8003/api/wachstumsprognose/berechnen", timeout=2)
        if api_response.status_code == 200:
            api_status = "✅ Backend-API erreichbar"
        else:
            api_status = f"⚠️ Backend-API Status: {api_response.status_code}"
    except:
        api_status = "❌ Backend-API nicht erreichbar"
    
    full_status = html.Div([
        html.P(status, style={'margin': '5px 0', 'fontSize': '16px'}),
        html.P(f"API-Status: {api_status}", style={'margin': '5px 0', 'fontSize': '12px', 'color': '#6c757d'}),
        html.P(f"Button-Klicks: {n_clicks}", style={'margin': '5px 0', 'fontSize': '12px', 'color': '#6c757d'})
    ])
    
    return (progress_container_style, progress_bar_style, text, full_status, button_disabled)

if __name__ == '__main__':
    print("🧪 CLAUDE_TEST: Starte Fortschrittsbalken-Demo...")
    print("📊 URL: http://10.1.1.110:8059")
    print("🎯 Zeigt wie Fortschrittsbalken aussehen sollten!")
    app.run(debug=False, host='0.0.0.0', port=8059)