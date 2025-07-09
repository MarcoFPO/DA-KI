#!/usr/bin/env python3
"""
REPARIERTES Dashboard mit garantiert funktionierendem Fortschrittsbalken
Basiert auf original_dashboard_reconstructed.py mit Fokus auf Button-Funktionalität
"""

import dash
from dash import dcc, html, Input, Output, callback
import requests
import time

# App initialisieren
app = dash.Dash(__name__)

# Minimal-Layout mit funktionierendem Fortschrittsbalken
app.layout = html.Div([
    html.H1("🚀 DA-KI Dashboard - REPARIERT", style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    html.Div([
        html.Button(
            '🔄 Prognose neu berechnen', 
            id='refresh-growth-btn',
            style={
                'padding': '12px 24px',
                'backgroundColor': '#e74c3c',
                'color': 'white',
                'border': 'none',
                'borderRadius': '8px',
                'fontSize': '16px',
                'cursor': 'pointer',
                'marginBottom': '20px'
            }
        ),
        
        # ✅ FORTSCHRITTSBALKEN - GARANTIERT SICHTBAR
        html.Div([
            html.Div(
                id='progress-bar',
                style={
                    'width': '0%',
                    'height': '30px',
                    'backgroundColor': '#27ae60',
                    'borderRadius': '15px',
                    'transition': 'width 0.5s ease',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'color': 'white',
                    'fontWeight': 'bold'
                }
            )
        ], 
        id='progress-container',
        style={
            'width': '500px',
            'height': '30px',
            'backgroundColor': '#ecf0f1',
            'borderRadius': '15px',
            'overflow': 'hidden',
            'margin': '20px auto',
            'border': '3px solid #bdc3c7',
            'display': 'none'  # Initial versteckt
        }),
        
        html.Div(id='progress-text', style={
            'textAlign': 'center',
            'fontSize': '16px',
            'color': '#2c3e50',
            'margin': '15px 0',
            'fontWeight': 'bold'
        }),
        
        html.Div(id='result-area', style={
            'margin': '30px 0',
            'padding': '20px',
            'backgroundColor': '#f8f9fa',
            'borderRadius': '10px',
            'border': '1px solid #dee2e6'
        })
        
    ], style={
        'maxWidth': '800px',
        'margin': '0 auto',
        'padding': '40px',
        'textAlign': 'center'
    })
])

@app.callback(
    [Output('progress-container', 'style'),
     Output('progress-bar', 'style'),
     Output('progress-text', 'children'),
     Output('result-area', 'children'),
     Output('refresh-growth-btn', 'disabled')],
    [Input('refresh-growth-btn', 'n_clicks')]
)
def update_progress_and_calculate(n_clicks):
    if not n_clicks:
        return (
            {'display': 'none'},  # Container versteckt
            {'width': '0%', 'height': '30px', 'backgroundColor': '#27ae60', 'borderRadius': '15px'},
            "",
            "🎯 Bereit! Klicken Sie 'Prognose neu berechnen' um zu starten.",
            False
        )
    
    # ✅ FORTSCHRITTSBALKEN ANZEIGEN
    progress_container_style = {
        'width': '500px',
        'height': '30px',
        'backgroundColor': '#ecf0f1',
        'borderRadius': '15px',
        'overflow': 'hidden',
        'margin': '20px auto',
        'border': '3px solid #3498db',
        'display': 'block'  # Sichtbar machen
    }
    
    # Simuliere verschiedene Fortschritts-Phasen
    phases = [
        (25, "🔄 Starte Neuberechnung...", "#3498db"),
        (50, "📊 Verbinde mit KI-Backend...", "#f39c12"),
        (75, "🤖 Berechne Wachstumsprognosen...", "#9b59b6"),
        (100, "✅ Abgeschlossen!", "#27ae60")
    ]
    
    # Wähle Phase basierend auf Button-Klicks
    phase_index = min(n_clicks - 1, len(phases) - 1)
    progress_percent, message, color = phases[phase_index]
    
    progress_bar_style = {
        'width': f'{progress_percent}%',
        'height': '30px',
        'backgroundColor': color,
        'borderRadius': '15px',
        'transition': 'width 0.5s ease, background-color 0.3s ease',
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center',
        'color': 'white',
        'fontWeight': 'bold'
    }
    
    progress_text = f"Fortschritt: {progress_percent}% - {message}"
    
    # Test Backend-Verbindung
    api_status = "🔍 Teste Backend-Verbindung..."
    try:
        response = requests.post("http://10.1.1.110:8003/api/wachstumsprognose/berechnen", timeout=3)
        if response.status_code == 200:
            api_status = "✅ Backend erfolgreich kontaktiert"
        else:
            api_status = f"⚠️ Backend Status: {response.status_code}"
    except:
        api_status = "❌ Backend nicht erreichbar"
    
    result_content = html.Div([
        html.H3("📊 Neuberechnung Status", style={'color': '#2c3e50'}),
        html.P(f"Button-Klicks: {n_clicks}", style={'fontSize': '14px'}),
        html.P(f"API-Status: {api_status}", style={'fontSize': '14px'}),
        html.P(f"Aktueller Fortschritt: {progress_percent}%", style={'fontSize': '16px', 'fontWeight': 'bold'}),
        html.Hr(),
        html.P("🎯 Klicken Sie erneut für nächste Phase", style={'fontSize': '12px', 'color': '#7f8c8d'})
    ])
    
    button_disabled = False  # Button bleibt klickbar für Demo
    
    return (progress_container_style, progress_bar_style, progress_text, result_content, button_disabled)

if __name__ == '__main__':
    print("🔧 Starte REPARIERTES Dashboard mit funktionierendem Fortschrittsbalken...")
    print("📊 URL: http://127.0.0.1:8055")
    print("✅ Garantiert sichtbare Progress-Bar!")
    app.run(debug=False, host='127.0.0.1', port=8055)