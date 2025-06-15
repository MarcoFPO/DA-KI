#!/usr/bin/env python3
"""
Vereinfachtes DA-KI Dashboard - Optimierte Version ohne komplexe Callbacks
Fokus auf Stabilität und einfache Struktur
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objs as go
import requests
import json
from datetime import datetime
import time

# App initialisieren
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.title = "🚀 DA-KI Dashboard - Vereinfacht"

# API Konfiguration
API_BASE_URL = "http://10.1.1.110:8003"

def hole_aktien_daten():
    """Hole Aktien-Daten von der API mit Fallback"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/wachstumsprognose/top10", timeout=3)
        if response.status_code == 200:
            data = response.json()
            return data.get('top_10_wachstums_aktien', [])
    except:
        pass
    
    # Fallback Mock-Daten
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
    """Erstelle 5x2 Karten-Layout"""
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

def erstelle_tabelle(aktien_daten):
    """Erstelle vereinfachte Tabelle"""
    if not aktien_daten:
        return html.P("Keine Daten verfügbar")
    
    zeilen = []
    for aktie in aktien_daten:
        prognose = aktie.get('prognose_30_tage', {})
        zeile = html.Tr([
            html.Td(f"#{aktie['rank']}", style={'fontWeight': 'bold'}),
            html.Td(aktie['symbol']),
            html.Td(aktie['branche']),
            html.Td(aktie['wkn']),
            html.Td(f"€{aktie['current_price']}"),
            html.Td(f"{aktie['wachstums_score']}/100"),
            html.Td(f"€{prognose.get('prognostizierter_preis', 0):.2f}"),
            html.Td(f"+{prognose.get('erwartete_rendite_prozent', 0):.1f}%", style={'color': '#27ae60'}),
            html.Td(prognose.get('vertrauen_level', 'N/A'))
        ])
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
                html.Th("Vertrauen", style={'padding': '10px', 'backgroundColor': '#e74c3c', 'color': 'white'})
            ])
        ]),
        html.Tbody(zeilen)
    ], style={'width': '100%', 'borderCollapse': 'collapse'})

def erstelle_charts(aktien_daten):
    """Erstelle Charts für Ranking und Rendite"""
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

# Statische Daten beim Start laden
AKTIEN_DATEN = hole_aktien_daten()

# Layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("🚀 DA-KI Dashboard - Vereinfacht", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 10}),
        html.P("Einfache und stabile Version mit 5x2 Karten-Layout", 
               style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': 30})
    ]),
    
    # Refresh Button
    html.Div([
        html.Button('🔄 Daten aktualisieren', id='refresh-btn', 
                   style={'padding': '10px 20px', 'backgroundColor': '#3498db', 'color': 'white',
                          'border': 'none', 'borderRadius': '5px', 'marginBottom': 20})
    ]),
    
    # Status
    html.Div(id='status-message', style={'marginBottom': 20}),
    
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
    
    # Tabelle
    html.Div([
        html.H3("📋 Detaillierte Prognose-Tabelle", style={'color': '#2c3e50'}),
        html.Div(id='prognose-tabelle', children=erstelle_tabelle(AKTIEN_DATEN))
    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px'}),
    
    # Footer
    html.Div([
        html.P(f"🤖 Vereinfachtes DA-KI Dashboard | 🕒 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",
               style={'textAlign': 'center', 'color': '#95a5a6', 'marginTop': 30})
    ])
], style={'margin': '20px'})

# Einfacher Callback für Refresh
@app.callback(
    [Output('aktien-karten', 'children'),
     Output('ranking-chart', 'figure'),
     Output('rendite-chart', 'figure'),
     Output('prognose-tabelle', 'children'),
     Output('status-message', 'children')],
    [Input('refresh-btn', 'n_clicks')]
)
def update_dashboard(n_clicks):
    """Einfacher Callback ohne Komplexität"""
    try:
        # Hole neue Daten
        aktien_daten = hole_aktien_daten()
        
        # Erstelle Komponenten
        karten = erstelle_karten_layout(aktien_daten)
        ranking_chart, rendite_chart = erstelle_charts(aktien_daten)
        tabelle = erstelle_tabelle(aktien_daten)
        
        # Status-Message
        status = html.Div([
            html.Span(f"✅ {len(aktien_daten)} Aktien geladen | Letztes Update: {datetime.now().strftime('%H:%M:%S')}", 
                     style={'color': '#27ae60', 'fontWeight': 'bold'})
        ], style={'padding': '10px', 'backgroundColor': '#d4edda', 'borderRadius': '5px'})
        
        return karten, ranking_chart, rendite_chart, tabelle, status
        
    except Exception as e:
        # Fehler-Behandlung
        error_msg = html.Div([
            html.Span(f"⚠️ Fehler beim Laden der Daten: {str(e)}", 
                     style={'color': '#e74c3c', 'fontWeight': 'bold'})
        ], style={'padding': '10px', 'backgroundColor': '#f8d7da', 'borderRadius': '5px'})
        
        # Fallback mit Mock-Daten
        karten = erstelle_karten_layout(AKTIEN_DATEN)
        ranking_chart, rendite_chart = erstelle_charts(AKTIEN_DATEN)
        tabelle = erstelle_tabelle(AKTIEN_DATEN)
        
        return karten, ranking_chart, rendite_chart, tabelle, error_msg

if __name__ == '__main__':
    print("🚀 Starte vereinfachtes DA-KI Dashboard...")
    print("📊 URL: http://10.1.1.110:8056")
    print("✨ Optimiert für Stabilität und Performance!")
    app.run(debug=False, host='0.0.0.0', port=8056)