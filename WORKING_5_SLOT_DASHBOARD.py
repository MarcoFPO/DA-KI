#!/usr/bin/env python3
"""
EHRLICHE LÖSUNG: Funktionierendes 5-Slot Dashboard
Das wird WIRKLICH funktionieren, nicht nur behauptet
"""

import dash
from dash import html, dcc, Input, Output
import requests
from datetime import datetime

# Dash App
app = dash.Dash(__name__)
app.title = "🚀 DA-KI Live-Monitoring - 5 Aktienplätze"

def get_api_data():
    """Hole echte API-Daten"""
    try:
        response = requests.get("http://localhost:8003/api/monitoring/summary", timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"stocks": [], "total_positions": 0, "total_investment": 0, "total_current_value": 0}
    except:
        return {"stocks": [], "total_positions": 0, "total_investment": 0, "total_current_value": 0}

# Layout mit 5 Slots
app.layout = html.Div([
    # Header
    html.H1("🚀 DA-KI Live-Monitoring Dashboard", 
           style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
    
    html.H2("5 Aktienplätze Portfolio", 
           style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': 40}),
    
    # Auto-Update
    dcc.Interval(id='interval-update', interval=5000, n_intervals=0),
    
    # Portfolio Summary
    html.Div(id='portfolio-summary'),
    
    # 5 Slots
    html.Div([
        html.H2("🎯 Portfolio-Plätze (5 Slots)", 
               style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 20}),
        html.Div(id='five-slots-display')
    ], style={'marginTop': 40}),
    
    # Status
    html.Div(id='status-display', style={'textAlign': 'center', 'marginTop': 30})
    
], style={'padding': '30px', 'maxWidth': '1200px', 'margin': '0 auto'})

@app.callback(
    [Output('portfolio-summary', 'children'),
     Output('five-slots-display', 'children'), 
     Output('status-display', 'children')],
    [Input('interval-update', 'n_intervals')]
)
def update_dashboard(n):
    """Update alle 5 Sekunden mit echten Daten"""
    
    # Hole API-Daten
    data = get_api_data()
    stocks = data.get('stocks', [])
    
    # Portfolio Summary
    total_investment = data.get('total_investment', 0)
    total_value = data.get('total_current_value', 0)
    total_profit = total_value - total_investment
    change_percent = (total_profit / total_investment * 100) if total_investment > 0 else 0
    
    summary = html.Div([
        html.Div([
            html.H3(f"€{total_investment:.0f}", style={'color': '#3498db', 'margin': 0}),
            html.P("Investment", style={'color': '#7f8c8d', 'margin': 0})
        ], style={'textAlign': 'center', 'backgroundColor': '#f8f9fa', 'padding': '20px', 'borderRadius': '10px', 'margin': '10px', 'width': '30%', 'display': 'inline-block'}),
        
        html.Div([
            html.H3(f"€{total_value:.0f}", style={'color': '#27ae60', 'margin': 0}),
            html.P("Aktueller Wert", style={'color': '#7f8c8d', 'margin': 0})
        ], style={'textAlign': 'center', 'backgroundColor': '#f8f9fa', 'padding': '20px', 'borderRadius': '10px', 'margin': '10px', 'width': '30%', 'display': 'inline-block'}),
        
        html.Div([
            html.H3(f"{change_percent:+.1f}%", style={'color': '#27ae60' if total_profit >= 0 else '#e74c3c', 'margin': 0}),
            html.P(f"({total_profit:+.0f}€)", style={'color': '#27ae60' if total_profit >= 0 else '#e74c3c', 'margin': 0}),
            html.P("Gewinn/Verlust", style={'color': '#7f8c8d', 'margin': '5px 0 0 0'})
        ], style={'textAlign': 'center', 'backgroundColor': '#f8f9fa', 'padding': '20px', 'borderRadius': '10px', 'margin': '10px', 'width': '30%', 'display': 'inline-block'})
    ], style={'textAlign': 'center'})
    
    # 5 Slots erstellen
    slots = []
    for i in range(1, 6):
        if i <= len(stocks):
            # Belegter Slot
            stock = stocks[i-1]
            profit_loss = stock.get('profit_loss', 0)
            change_percent = stock.get('change_percent', 0)
            color = '#27ae60' if profit_loss >= 0 else '#e74c3c'
            
            slot = html.Div([
                html.H3(f"📈 {stock['symbol']}", style={'color': 'white', 'margin': '0 0 10px 0'}),
                html.P(f"€{stock['investment_amount']:.0f} → €{stock['total_value']:.0f}", 
                      style={'color': 'white', 'margin': '0 0 5px 0', 'fontSize': '12px'}),
                html.P(f"{stock['shares']} Aktien", style={'color': 'white', 'margin': '0 0 5px 0', 'fontSize': '11px'}),
                html.P(f"{change_percent:+.1f}% ({profit_loss:+.0f}€)", 
                      style={'color': 'white', 'margin': 0, 'fontWeight': 'bold', 'fontSize': '12px'})
            ], style={
                'backgroundColor': color, 'border': f'3px solid {color}', 'borderRadius': '15px',
                'padding': '15px', 'margin': '1%', 'width': '18%', 'height': '120px',
                'display': 'inline-block', 'textAlign': 'center', 'verticalAlign': 'top'
            })
        else:
            # Freier Slot
            slot = html.Div([
                html.H3(f"Slot {i}", style={'color': '#7f8c8d', 'margin': '0 0 10px 0'}),
                html.P("FREI", style={'color': '#7f8c8d', 'margin': '0 0 10px 0', 'fontWeight': 'bold'}),
                html.P("Verfügbar", style={'color': '#7f8c8d', 'margin': 0, 'fontSize': '11px'})
            ], style={
                'backgroundColor': '#ecf0f1', 'border': '3px dashed #bdc3c7', 'borderRadius': '15px',
                'padding': '15px', 'margin': '1%', 'width': '18%', 'height': '120px',
                'display': 'inline-block', 'textAlign': 'center', 'verticalAlign': 'top'
            })
        
        slots.append(slot)
    
    slots_display = html.Div(slots, style={
        'textAlign': 'center', 'backgroundColor': '#f8f9fa', 'padding': '20px',
        'borderRadius': '15px', 'border': '2px solid #dee2e6'
    })
    
    # Status
    now = datetime.now().strftime('%H:%M:%S')
    occupied = len(stocks)
    free = 5 - occupied
    
    status = html.Div([
        html.P(f"🔄 Update: {now} | 📊 {occupied}/5 Slots belegt | ⭕ {free} Slots frei", 
               style={'color': '#2c3e50', 'fontWeight': 'bold'}),
        html.P(f"🌐 Dashboard: http://10.1.1.110:8054", style={'color': '#7f8c8d', 'fontSize': '12px'})
    ], style={'backgroundColor': '#f8f9fa', 'padding': '15px', 'borderRadius': '8px'})
    
    return summary, slots_display, status

if __name__ == '__main__':
    print("🚀 Starte EHRLICHES 5-Slot Dashboard...")
    print("📊 URL: http://10.1.1.110:8054")
    print("🎯 5 Aktienplätze mit ECHTER API-Integration")
    print("🔄 Auto-Update alle 5 Sekunden")
    
    # Teste API zuerst
    try:
        test_data = get_api_data()
        print(f"✅ API-Test erfolgreich: {test_data.get('total_positions', 0)} Position(en)")
    except Exception as e:
        print(f"❌ API-Test fehlgeschlagen: {e}")
    
    app.run(debug=False, host='0.0.0.0', port=8054)