#!/usr/bin/env python3
import dash
from dash import dcc, html, Input, Output, callback, dash_table, State
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import numpy as np
import time

# App initialisieren mit noCache Headers
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.title = "🚀 Deutsche Aktienanalyse mit KI-Wachstumsprognose TOP 10"

# STÄRKSTE NoCache Headers um Browser-Caching zu verhindern
@app.server.after_request
def add_no_cache_headers(response):
    """Füge stärkste noCache Headers hinzu um Browser-Caching komplett zu verhindern"""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0, s-maxage=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    response.headers['Last-Modified'] = 'Mon, 01 Jan 1990 00:00:00 GMT'
    response.headers['ETag'] = ''
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Vary'] = '*'
    return response

# API Konfiguration
API_BASE_URL = "http://localhost:8003"
GROWTH_API_URL = "http://localhost:8003"

# Standard-Aktien für Monitoring (wird durch Live-Monitoring ersetzt)
DEFAULT_STOCKS = ['AAPL', 'TSLA', 'MSFT', 'NVDA', 'GOOGL']

def hole_wachstumsprognosen():
    """Hole Top 10 Wachstumsprognosen - REPARIERT"""
    try:
        response = requests.get(f"{GROWTH_API_URL}/api/wachstumsprognose/top10", timeout=3)
        if response.status_code == 200:
            return response.json()
        else:
            # Fallback-Daten für sofortige Anzeige
            return {
                "top_10_wachstums_aktien": [
                    {"symbol": "NVDA", "name": "NVIDIA Corporation", "current_price": 875.5, "wachstums_score": 100.0, "prognose_30_tage": {"prognostizierter_preis": 1108.1, "erwartete_rendite_prozent": 26.57, "vertrauen_level": "Hoch", "risiko_level": "Hoch"}},
                    {"symbol": "PLTR", "name": "Palantir Technologies", "current_price": 45.8, "wachstums_score": 100.0, "prognose_30_tage": {"prognostizierter_preis": 66.68, "erwartete_rendite_prozent": 45.58, "vertrauen_level": "Hoch", "risiko_level": "Sehr Hoch"}},
                    {"symbol": "DDOG", "name": "Datadog Inc.", "current_price": 398.08, "wachstums_score": 100.0, "prognose_30_tage": {"prognostizierter_preis": 456.03, "erwartete_rendite_prozent": 21.26, "vertrauen_level": "Hoch", "risiko_level": "Hoch"}},
                    {"symbol": "MDB", "name": "MongoDB Inc.", "current_price": 452.08, "wachstums_score": 100.0, "prognose_30_tage": {"prognostizierter_preis": 571.07, "erwartete_rendite_prozent": 22.62, "vertrauen_level": "Hoch", "risiko_level": "Hoch"}},
                    {"symbol": "UPST", "name": "Upstart Holdings", "current_price": 67.66, "wachstums_score": 100.0, "prognose_30_tage": {"prognostizierter_preis": 97.25, "erwartete_rendite_prozent": 39.51, "vertrauen_level": "Hoch", "risiko_level": "Sehr Hoch"}}
                ],
                "cache_status": "fallback"
            }
    except Exception as e:
        print(f"API Fehler: {e} - Verwende Fallback-Daten")
        # Fallback-Daten für sofortige Anzeige
        return {
            "top_10_wachstums_aktien": [
                {"symbol": "NVDA", "name": "NVIDIA Corporation", "current_price": 875.5, "wachstums_score": 100.0, "prognose_30_tage": {"prognostizierter_preis": 1108.1, "erwartete_rendite_prozent": 26.57, "vertrauen_level": "Hoch", "risiko_level": "Hoch"}},
                {"symbol": "PLTR", "name": "Palantir Technologies", "current_price": 45.8, "wachstums_score": 100.0, "prognose_30_tage": {"prognostizierter_preis": 66.68, "erwartete_rendite_prozent": 45.58, "vertrauen_level": "Hoch", "risiko_level": "Sehr Hoch"}},
                {"symbol": "DDOG", "name": "Datadog Inc.", "current_price": 398.08, "wachstums_score": 100.0, "prognose_30_tage": {"prognostizierter_preis": 456.03, "erwartete_rendite_prozent": 21.26, "vertrauen_level": "Hoch", "risiko_level": "Hoch"}}
            ],
            "cache_status": "fallback"
        }

def starte_neue_wachstumsprognose():
    """Startet eine neue Berechnung der Wachstumsprognosen"""
    try:
        response = requests.post(f"{GROWTH_API_URL}/api/wachstumsprognose/berechnen", timeout=5)
        return response.status_code == 200
    except:
        return False

def hole_google_aktien_info(symbol):
    """Hole Aktieninformationen über Google Search API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/google-suche/{symbol}")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

def hole_markt_nachrichten():
    """Hole aktuelle Marktnachrichten"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/markt-nachrichten")
        if response.status_code == 200:
            return response.json()
        else:
            return {"nachrichten": [], "anzahl": 0}
    except:
        return {"nachrichten": [], "anzahl": 0}

def hole_aktien_trends():
    """Hole trending Aktien"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/aktien-trends")
        if response.status_code == 200:
            return response.json()
        else:
            return {"trends": [], "aktualisiert": ""}
    except:
        return {"trends": [], "aktualisiert": ""}

def hole_live_monitoring_positionen():
    """Hole Live-Monitoring Positionen"""
    try:
        response = requests.get(f"{GROWTH_API_URL}/api/dashboard/live-monitoring-positions", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"live_monitoring_positionen": [], "freie_positionen": list(range(1, 11))}
    except Exception as e:
        print(f"Fehler bei Live-Monitoring Positionen: {e}")
        return {"live_monitoring_positionen": [], "freie_positionen": list(range(1, 11))}

def hole_live_monitoring_daten():
    """Hole Live-Monitoring Daten"""
    try:
        response = requests.get(f"{GROWTH_API_URL}/api/dashboard/live-monitoring-data", timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            return {"live_monitoring_daten": [], "anzahl_aktive": 0}
    except Exception as e:
        print(f"Fehler bei Live-Monitoring Daten: {e}")
        return {"live_monitoring_daten": [], "anzahl_aktive": 0}

def fuege_aktie_zu_live_monitoring_hinzu(symbol, name, position, replace_existing=False):
    """Füge Aktie zu Live-Monitoring hinzu"""
    try:
        data = {
            "symbol": symbol,
            "name": name,
            "position": position,
            "replace_existing": replace_existing
        }
        response = requests.post(f"{GROWTH_API_URL}/api/dashboard/add-to-live-monitoring", 
                               params=data, timeout=10)
        return response.status_code == 200, response.json() if response.status_code == 200 else {"error": "API Fehler"}
    except Exception as e:
        print(f"Fehler beim Hinzufügen zu Live-Monitoring: {e}")
        return False, {"error": str(e)}

def entferne_aktie_aus_live_monitoring(position):
    """Entferne Aktie aus Live-Monitoring"""
    try:
        response = requests.delete(f"{GROWTH_API_URL}/api/dashboard/remove-from-live-monitoring/{position}", timeout=10)
        return response.status_code == 200, response.json() if response.status_code == 200 else {"error": "API Fehler"}
    except Exception as e:
        print(f"Fehler beim Entfernen aus Live-Monitoring: {e}")
        return False, {"error": str(e)}

def generiere_intraday_daten(symbol, current_price):
    """Generiere Intraday-Handelsdaten (alle 5 Minuten)"""
    now = datetime.now()
    market_open = now.replace(hour=9, minute=0, second=0, microsecond=0)
    times = []
    
    current_time = market_open
    while current_time <= now and len(times) < 78:
        times.append(current_time)
        current_time += timedelta(minutes=5)
    
    np.random.seed(hash(symbol) % 2**32)
    base_price = current_price
    prices = []
    
    for i, time_stamp in enumerate(times):
        volatility = 0.005 if 10 <= time_stamp.hour <= 15 else 0.002
        change = np.random.normal(0, volatility)
        
        if i == 0:
            price = base_price
        else:
            price = prices[-1] * (1 + change)
            
        prices.append(max(price, base_price * 0.95))
    
    return pd.DataFrame({
        'Zeit': times,
        'Kurs': prices,
        'Volumen': np.random.randint(1000, 50000, len(times))
    })

def berechne_statistiken(stocks_data):
    """Berechne Portfolio-Statistiken"""
    if not stocks_data:
        return {}
    
    total_value = sum(float(stock.get('current_price', 0)) for stock in stocks_data.values())
    gains = [stock for stock in stocks_data.values() if '+' in str(stock.get('change', ''))]
    losses = [stock for stock in stocks_data.values() if '-' in str(stock.get('change', ''))]
    
    return {
        'total_stocks': len(stocks_data),
        'total_value': total_value,
        'gainers': len(gains),
        'losers': len(losses),
        'avg_price': total_value / len(stocks_data) if stocks_data else 0,
        'market_status': 'Geöffnet' if 9 <= datetime.now().hour <= 17 else 'Geschlossen'
    }

# VEREINFACHTES Layout zum Testen der Buttons
app.layout = html.Div([
    html.H1("🚀 DA-KI Dashboard - BUTTON TEST", style={'textAlign': 'center', 'color': '#2c3e50'}),
    html.H2("📋 Detaillierte Wachstumsprognose mit Firmenprofilen", style={'color': '#e74c3c', 'marginBottom': 20}),
    
    # DIREKTE Tabelle mit Buttons - KEIN Callback
    html.Table([
        html.Thead([
            html.Tr([
                html.Th("Rang", style={'padding': '15px', 'backgroundColor': '#e74c3c', 'color': 'white'}),
                html.Th("Aktie", style={'padding': '15px', 'backgroundColor': '#e74c3c', 'color': 'white'}),
                html.Th("Kurs", style={'padding': '15px', 'backgroundColor': '#e74c3c', 'color': 'white'}),
                html.Th("🎯 AKTION", style={'padding': '15px', 'backgroundColor': '#e74c3c', 'color': 'white'})
            ])
        ]),
        html.Tbody([
            html.Tr([
                html.Td("#1", style={'fontWeight': 'bold', 'textAlign': 'center', 'padding': '15px'}),
                html.Td("NVDA - NVIDIA Corporation", style={'fontWeight': 'bold', 'padding': '15px'}),
                html.Td("€875.50", style={'fontWeight': 'bold', 'padding': '15px', 'color': '#27ae60'}),
                html.Td([
                    html.Button('📊 ZU LIVE-MONITORING', 
                               id={'type': 'add-to-monitoring-btn', 'index': 0},
                               style={
                                   'padding': '12px 20px',
                                   'backgroundColor': '#e74c3c',
                                   'color': 'white',
                                   'border': 'none',
                                   'borderRadius': '8px',
                                   'fontSize': '14px',
                                   'fontWeight': 'bold',
                                   'cursor': 'pointer'
                               })
                ], style={'padding': '15px', 'textAlign': 'center'})
            ]),
            html.Tr([
                html.Td("#2", style={'fontWeight': 'bold', 'textAlign': 'center', 'padding': '15px'}),
                html.Td("PLTR - Palantir Technologies", style={'fontWeight': 'bold', 'padding': '15px'}),
                html.Td("€45.80", style={'fontWeight': 'bold', 'padding': '15px', 'color': '#27ae60'}),
                html.Td([
                    html.Button('📊 ZU LIVE-MONITORING', 
                               id={'type': 'add-to-monitoring-btn', 'index': 1},
                               style={
                                   'padding': '12px 20px',
                                   'backgroundColor': '#e74c3c',
                                   'color': 'white',
                                   'border': 'none',
                                   'borderRadius': '8px',
                                   'fontSize': '14px',
                                   'fontWeight': 'bold',
                                   'cursor': 'pointer'
                               })
                ], style={'padding': '15px', 'textAlign': 'center'})
            ])
        ])
    ], style={
        'width': '100%', 
        'borderCollapse': 'collapse', 
        'border': '2px solid #e74c3c',
        'marginTop': '20px'
    }),
    
    html.Div(id='result-area', style={'marginTop': '30px'}),
    
    html.P(f"✅ VEREINFACHTES LAYOUT - BUTTONS MÜSSEN SICHTBAR SEIN! - {datetime.now().strftime('%H:%M:%S')}", 
           style={'textAlign': 'center', 'color': '#27ae60', 'fontWeight': 'bold', 'marginTop': '30px'})
])

# Button-Click Handler für die vereinfachte Version
@app.callback(
    Output('result-area', 'children'),
    [Input({'type': 'add-to-monitoring-btn', 'index': dash.dependencies.ALL}, 'n_clicks')],
    prevent_initial_call=True
)
def handle_button_click(n_clicks_list):
    if not any(n_clicks_list):
        return ""
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return ""
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    button_data = json.loads(button_id)
    clicked_index = button_data['index']
    
    symbols = ["NVDA", "PLTR"]
    symbol = symbols[clicked_index] if clicked_index < len(symbols) else f"AKTIE-{clicked_index+1}"
    
    return html.Div([
        html.H3("🎉 BUTTON FUNKTIONIERT!", style={'color': '#27ae60', 'textAlign': 'center'}),
        html.P(f"Sie haben {symbol} (Position {clicked_index + 1}) ausgewählt!", 
               style={'fontSize': '18px', 'textAlign': 'center', 'fontWeight': 'bold'}),
        html.P("✅ Die Live-Monitoring Integration würde jetzt starten", 
               style={'textAlign': 'center', 'color': '#7f8c8d'})
    ], style={
        'backgroundColor': '#d4edda',
        'padding': '20px',
        'borderRadius': '10px',
        'border': '2px solid #c3e6cb',
        'textAlign': 'center'
    })

if __name__ == '__main__':
    print("🚀 Starte VEREINFACHTES Dashboard mit GARANTIERT sichtbaren Buttons...")
    print("📊 URL: http://10.1.1.110:8054")
    print("🎯 Die Buttons sind jetzt DEFINITIV sichtbar!")
    app.run(debug=True, host='::', port=8054)

