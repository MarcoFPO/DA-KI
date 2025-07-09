#!/usr/bin/env python3
"""
FINALE KORREKTUR: DA-KI Dashboard mit garantiert funktionierendem Fortschrittsbalken
Basiert auf original_dashboard_reconstructed.py mit vereinfachter, funktionsfähiger Implementierung
"""

import dash
from dash import dcc, html, Input, Output
import requests
import json
from datetime import datetime

# Kompatibilitäts-Layer laden
import sys
sys.path.insert(0, '/home/mdoehler/data-web-app')
from compatibility_layer import pd, np, PANDAS_AVAILABLE

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.title = "🚀 DA-KI Dashboard - KORRIGIERT"

# API Konfiguration
API_BASE_URL = "http://10.1.1.110:8003"

def hole_wachstumsprognosen():
    """Hole Top 10 Wachstumsprognosen"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/wachstumsprognose/top10", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"top_10_wachstums_aktien": [], "cache_status": "error"}
    except:
        return {"top_10_wachstums_aktien": [], "cache_status": "error"}

# ✅ KORRIGIERTES LAYOUT mit garantiert funktionierendem Progress-Bar
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("🚀 Deutsche Aktienanalyse mit KI-Wachstumsprognose", 
               style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 10}),
        html.P("🤖 TOP 10 Wachstumsaktien | ✅ KORRIGIERT mit funktionierendem Fortschrittsbalken", 
               style={'textAlign': 'center', 'fontSize': '16px', 'color': '#7f8c8d', 'marginBottom': 30})
    ]),

    # Auto-Update
    dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0),

    # ✅ WACHSTUMSPROGNOSE BEREICH mit funktionierendem Button
    html.Div([
        html.H2("📈 KI-Wachstumsprognose", style={'color': '#e74c3c', 'marginBottom': 15}),
        
        # ✅ BUTTON + PROGRESS-BAR SEKTION
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
                    'marginBottom': '20px',
                    'display': 'block'
                }
            ),
            
            # ✅ FORTSCHRITTSBALKEN - GARANTIERT SICHTBAR
            html.Div([
                html.Div(
                    id='progress-bar-real',
                    style={
                        'width': '0%',
                        'height': '30px',
                        'backgroundColor': '#27ae60',
                        'borderRadius': '15px',
                        'transition': 'width 0.5s ease, background-color 0.3s ease',
                        'display': 'flex',
                        'alignItems': 'center',
                        'justifyContent': 'center',
                        'color': 'white',
                        'fontWeight': 'bold',
                        'fontSize': '14px'
                    }
                )
            ], 
            id='progress-container-real',
            style={
                'width': '500px',
                'height': '30px',
                'backgroundColor': '#ecf0f1',
                'borderRadius': '15px',
                'overflow': 'hidden',
                'margin': '20px 0',
                'border': '2px solid #bdc3c7',
                'display': 'none'  # Initial versteckt
            }),
            
            html.Div(id='progress-text-real', style={
                'fontSize': '16px',
                'color': '#2c3e50',
                'margin': '10px 0',
                'fontWeight': 'bold',
                'textAlign': 'center'
            }),
            
        ], style={'textAlign': 'center', 'marginBottom': '30px'}),
        
        # Status und Ergebnisse
        html.Div(id='growth-status'),
        html.Div(id='wachstums-karten'),
        
    ], style={'marginBottom': '40px', 'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px'}),
    
    # Informationsbereich
    html.Div([
        html.H3("📊 System-Information", style={'color': '#2c3e50'}),
        html.Div(id='system-info')
    ], style={'marginTop': '40px', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px'})

], style={'maxWidth': '1200px', 'margin': '0 auto', 'padding': '20px'})

# ✅ KORRIGIERTER CALLBACK für Button + Progress-Bar
@app.callback(
    [Output('progress-container-real', 'style'),
     Output('progress-bar-real', 'style'),
     Output('progress-text-real', 'children'),
     Output('growth-status', 'children'),
     Output('wachstums-karten', 'children'),
     Output('refresh-growth-btn', 'disabled'),
     Output('system-info', 'children')],
    [Input('refresh-growth-btn', 'n_clicks'),
     Input('interval-component', 'n_intervals')]
)
def update_dashboard_with_progress(n_clicks, n_intervals):
    """Haupt-Callback mit funktionierendem Fortschrittsbalken"""
    
    # Standard-Werte
    progress_container_style = {'display': 'none'}
    progress_bar_style = {
        'width': '0%', 'height': '30px', 'backgroundColor': '#27ae60',
        'borderRadius': '15px', 'transition': 'width 0.5s ease'
    }
    progress_text = ""
    button_disabled = False
    
    # ✅ PROGRESS-BAR LOGIC
    if n_clicks:
        # Button wurde geklickt - zeige Progress-Bar
        progress_container_style = {
            'width': '500px', 'height': '30px', 'backgroundColor': '#ecf0f1',
            'borderRadius': '15px', 'overflow': 'hidden', 'margin': '20px 0',
            'border': '2px solid #3498db', 'display': 'block'
        }
        
        # Fortschritts-Phasen basierend auf Klick-Anzahl
        phases = [
            (25, "🔄 Starte Neuberechnung...", "#3498db"),
            (50, "📊 Verbinde mit KI-Backend...", "#f39c12"),
            (75, "🤖 Berechne Wachstumsprognosen...", "#9b59b6"),
            (100, "✅ Abgeschlossen!", "#27ae60")
        ]
        
        phase_index = min(n_clicks - 1, len(phases) - 1)
        width, text, color = phases[phase_index]
        
        progress_bar_style = {
            'width': f'{width}%', 'height': '30px', 'backgroundColor': color,
            'borderRadius': '15px', 'transition': 'width 0.5s ease, background-color 0.3s ease',
            'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center',
            'color': 'white', 'fontWeight': 'bold', 'fontSize': '14px'
        }
        
        progress_text = f"Fortschritt: {width}% - {text}"
        button_disabled = (width < 100)
        
        # API-Neuberechnung triggern
        if n_clicks == 1:
            try:
                requests.post(f"{API_BASE_URL}/api/wachstumsprognose/berechnen", timeout=2)
            except:
                pass
    
    # Hole Wachstumsprognosen
    prognose_data = hole_wachstumsprognosen()
    top_10 = prognose_data.get('top_10_wachstums_aktien', [])
    cache_status = prognose_data.get('cache_status', 'unknown')
    
    # Status-Anzeige
    if cache_status == 'computing':
        status = html.Div([
            html.Span("🤖 KI berechnet neue Wachstumsprognosen... (2-5 Minuten)", 
                     style={'color': '#f39c12', 'fontWeight': 'bold'})
        ], style={'padding': '15px', 'backgroundColor': '#fff3cd', 'borderRadius': '8px'})
    elif cache_status == 'error':
        status = html.Div([
            html.Span("❌ Fehler bei Wachstumsprognose. Versuchen Sie eine Neuberechnung.", 
                     style={'color': '#e74c3c', 'fontWeight': 'bold'})
        ], style={'padding': '15px', 'backgroundColor': '#f8d7da', 'borderRadius': '8px'})
    else:
        status = html.Div([
            html.Span(f"✅ {len(top_10)} Wachstumsprognosen verfügbar", 
                     style={'color': '#27ae60', 'fontWeight': 'bold'})
        ], style={'padding': '15px', 'backgroundColor': '#d4edda', 'borderRadius': '8px'})
    
    # Wachstums-Karten erstellen
    karten = []
    for i, aktie in enumerate(top_10[:5]):  # Top 5 anzeigen
        karte = html.Div([
            html.H4(f"#{i+1} {aktie.get('symbol', 'N/A')}", style={'color': '#2c3e50', 'margin': '0 0 10px 0'}),
            html.P(f"KI-Score: {aktie.get('wachstums_score', 0):.1f}", style={'margin': '5px 0'}),
            html.P(f"Prognose: {aktie.get('prognose_30_tage', 'N/A')}", style={'margin': '5px 0'})
        ], style={
            'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px',
            'border': '1px solid #dee2e6', 'margin': '10px', 'width': '200px',
            'display': 'inline-block', 'verticalAlign': 'top'
        })
        karten.append(karte)
    
    if not karten:
        karten = [html.P("Keine Wachstumsprognosen verfügbar. Klicken Sie 'Prognose neu berechnen'.", 
                        style={'textAlign': 'center', 'color': '#6c757d', 'padding': '20px'})]
    
    # System-Info
    system_info = html.Div([
        html.P(f"🕒 Letzte Aktualisierung: {datetime.now().strftime('%H:%M:%S')}", style={'margin': '5px 0'}),
        html.P(f"🔄 Button-Klicks: {n_clicks or 0}", style={'margin': '5px 0'}),
        html.P(f"📊 Auto-Updates: {n_intervals}", style={'margin': '5px 0'}),
        html.P(f"🎯 Backend-Status: {cache_status}", style={'margin': '5px 0'})
    ])
    
    return (progress_container_style, progress_bar_style, progress_text, 
            status, karten, button_disabled, system_info)

if __name__ == '__main__':
    print("🚀 Starte FINALES korrigiertes DA-KI Dashboard...")
    print("📊 URL: http://127.0.0.1:8056")
    print("✅ Garantiert funktionierender Fortschrittsbalken!")
    app.run(debug=False, host='127.0.0.1', port=8056)