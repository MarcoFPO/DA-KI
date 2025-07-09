#!/usr/bin/env python3
"""
Test für Prognose-Neuberechnung und Fortschrittsbalken
"""

import sys
import os
sys.path.append('/home/mdoehler/data-web-app/frontend')

from dash import Dash, html, dcc, Input, Output, callback
import requests
import time

app = Dash(__name__)

app.layout = html.Div([
    html.H1("🔄 Test: Prognose neu berechnen"),
    html.Button("🔄 Prognose neu berechnen", id='test-refresh-btn', 
                style={'padding': '10px 20px', 'backgroundColor': '#3498db', 'color': 'white', 
                       'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer'}),
    html.Div([
        html.Div([
            html.Div(id='test-progress-bar', style={
                'width': '0%', 'height': '20px', 'backgroundColor': '#27ae60', 
                'borderRadius': '10px', 'transition': 'width 0.3s ease'
            })
        ], id='test-progress-container', style={
            'width': '300px', 'height': '20px', 'backgroundColor': '#ecf0f1',
            'borderRadius': '10px', 'overflow': 'hidden', 'margin': '20px', 'display': 'none'
        }),
        html.Div(id='test-progress-text', style={'fontSize': '12px', 'color': '#7f8c8d'})
    ]),
    html.Div(id='test-status-message', style={'margin': '20px'}),
    dcc.Interval(
        id='test-interval',
        interval=1000,  # Update every second
        n_intervals=0,
        disabled=True
    )
])

@app.callback(
    [Output('test-progress-container', 'style'),
     Output('test-progress-bar', 'style'),
     Output('test-progress-text', 'children'),
     Output('test-status-message', 'children'),
     Output('test-refresh-btn', 'disabled'),
     Output('test-interval', 'disabled')],
    [Input('test-refresh-btn', 'n_clicks'),
     Input('test-interval', 'n_intervals')]
)
def update_progress(n_clicks, n_intervals):
    import dash
    ctx = dash.callback_context
    
    if not ctx.triggered:
        # Initial state
        return (
            {'display': 'none'},
            {'width': '0%', 'height': '20px', 'backgroundColor': '#27ae60', 'borderRadius': '10px'},
            "",
            "Bereit zum Testen",
            False,
            True
        )
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'test-refresh-btn' and n_clicks:
        # Button wurde geklickt - starte Neuberechnung
        try:
            # Teste API-Verbindung
            response = requests.post("http://10.1.1.110:8003/api/wachstumsprognose/recalculate", timeout=5)
            
            if response.status_code == 200:
                # Erfolgreich gestartet
                progress_container_style = {
                    'width': '300px', 'height': '20px', 'backgroundColor': '#ecf0f1',
                    'borderRadius': '10px', 'overflow': 'hidden', 'margin': '20px', 'display': 'block'
                }
                progress_bar_style = {
                    'width': '10%', 'height': '20px', 'backgroundColor': '#3498db',
                    'borderRadius': '10px', 'transition': 'width 0.3s ease'
                }
                progress_text = "🔄 Neuberechnung gestartet..."
                status_message = "✅ Prognose-Neuberechnung erfolgreich gestartet!"
                button_disabled = True
                interval_disabled = False
                
                return (progress_container_style, progress_bar_style, progress_text, status_message, button_disabled, interval_disabled)
            else:
                # API-Fehler
                status_message = f"❌ API-Fehler: {response.status_code}"
                return (
                    {'display': 'none'},
                    {'width': '0%', 'height': '20px', 'backgroundColor': '#27ae60', 'borderRadius': '10px'},
                    "",
                    status_message,
                    False,
                    True
                )
        except requests.exceptions.ConnectionError:
            # Teste mit alternativer API-Route
            try:
                response = requests.post("http://10.1.1.110:8003/api/wachstumsprognose/berechnen", timeout=5)
                if response.status_code == 200:
                    progress_container_style = {
                        'width': '300px', 'height': '20px', 'backgroundColor': '#ecf0f1',
                        'borderRadius': '10px', 'overflow': 'hidden', 'margin': '20px', 'display': 'block'
                    }
                    progress_bar_style = {
                        'width': '10%', 'height': '20px', 'backgroundColor': '#3498db',
                        'borderRadius': '10px', 'transition': 'width 0.3s ease'
                    }
                    progress_text = "🔄 Neuberechnung gestartet (alternative Route)..."
                    status_message = "✅ Prognose-Neuberechnung erfolgreich gestartet (alternative API)!"
                    button_disabled = True
                    interval_disabled = False
                    
                    return (progress_container_style, progress_bar_style, progress_text, status_message, button_disabled, interval_disabled)
            except:
                pass
            
            status_message = "❌ Verbindung zur API fehlgeschlagen"
            return (
                {'display': 'none'},
                {'width': '0%', 'height': '20px', 'backgroundColor': '#27ae60', 'borderRadius': '10px'},
                "",
                status_message,
                False,
                True
            )
        except Exception as e:
            status_message = f"❌ Fehler: {str(e)}"
            return (
                {'display': 'none'},
                {'width': '0%', 'height': '20px', 'backgroundColor': '#27ae60', 'borderRadius': '10px'},
                "",
                status_message,
                False,
                True
            )
    
    elif trigger_id == 'test-interval':
        # Fortschritt überwachen
        try:
            # Versuche Progress-API
            response = requests.get("http://10.1.1.110:8003/api/wachstumsprognose/progress", timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                progress = data.get('progress', 0)
                status = data.get('status', 'unknown')
                message = data.get('message', 'Berechnet...')
                
                if progress >= 100 or status == 'completed':
                    # Fertig
                    progress_container_style = {'display': 'none'}
                    progress_bar_style = {
                        'width': '100%', 'height': '20px', 'backgroundColor': '#27ae60',
                        'borderRadius': '10px', 'transition': 'width 0.3s ease'
                    }
                    progress_text = "✅ Abgeschlossen!"
                    status_message = "✅ Prognose-Neuberechnung abgeschlossen!"
                    button_disabled = False
                    interval_disabled = True
                    
                    return (progress_container_style, progress_bar_style, progress_text, status_message, button_disabled, interval_disabled)
                else:
                    # Läuft noch
                    progress_container_style = {
                        'width': '300px', 'height': '20px', 'backgroundColor': '#ecf0f1',
                        'borderRadius': '10px', 'overflow': 'hidden', 'margin': '20px', 'display': 'block'
                    }
                    progress_bar_style = {
                        'width': f'{progress}%', 'height': '20px', 'backgroundColor': '#3498db',
                        'borderRadius': '10px', 'transition': 'width 0.3s ease'
                    }
                    progress_text = f"{message} ({progress:.0f}%)"
                    status_message = f"🔄 {message}"
                    button_disabled = True
                    interval_disabled = False
                    
                    return (progress_container_style, progress_bar_style, progress_text, status_message, button_disabled, interval_disabled)
            else:
                # Progress-API nicht verfügbar - simuliere
                simulated_progress = min(95, (n_intervals * 3))  # 3% pro Sekunde
                
                if simulated_progress >= 95:
                    # Simuliert fertig
                    progress_container_style = {'display': 'none'}
                    progress_bar_style = {
                        'width': '100%', 'height': '20px', 'backgroundColor': '#27ae60',
                        'borderRadius': '10px', 'transition': 'width 0.3s ease'
                    }
                    progress_text = "✅ Abgeschlossen!"
                    status_message = "✅ Prognose-Neuberechnung abgeschlossen (simuliert)!"
                    button_disabled = False
                    interval_disabled = True
                    
                    return (progress_container_style, progress_bar_style, progress_text, status_message, button_disabled, interval_disabled)
                else:
                    # Läuft noch
                    progress_container_style = {
                        'width': '300px', 'height': '20px', 'backgroundColor': '#ecf0f1',
                        'borderRadius': '10px', 'overflow': 'hidden', 'margin': '20px', 'display': 'block'
                    }
                    progress_bar_style = {
                        'width': f'{simulated_progress}%', 'height': '20px', 'backgroundColor': '#3498db',
                        'borderRadius': '10px', 'transition': 'width 0.3s ease'
                    }
                    progress_text = f"📊 Berechne Prognosen... ({simulated_progress:.0f}%)"
                    status_message = f"🔄 Simulierte Berechnung läuft ({simulated_progress:.0f}%)"
                    button_disabled = True
                    interval_disabled = False
                    
                    return (progress_container_style, progress_bar_style, progress_text, status_message, button_disabled, interval_disabled)
                    
        except Exception as e:
            # Fehler beim Progress-Check
            status_message = f"⚠️ Progress-Check Fehler: {str(e)}"
            return (
                {'display': 'none'},
                {'width': '0%', 'height': '20px', 'backgroundColor': '#27ae60', 'borderRadius': '10px'},
                "",
                status_message,
                False,
                True
            )
    
    # Fallback
    return (
        {'display': 'none'},
        {'width': '0%', 'height': '20px', 'backgroundColor': '#27ae60', 'borderRadius': '10px'},
        "",
        "Warte auf Aktion...",
        False,
        True
    )

if __name__ == '__main__':
    print("🧪 Starte Test für Prognose-Neuberechnung...")
    print("📊 URL: http://10.1.1.110:8055")
    app.run(debug=False, host='0.0.0.0', port=8055)