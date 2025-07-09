#!/usr/bin/env python3
"""
FINALES Live-Monitoring Dashboard für 10.1.1.110:8054
Zeigt nur die 5-Slot Visualisierung mit echten API-Daten
"""

import dash
from dash import html, dcc, Input, Output, callback
import requests
import json
from datetime import datetime

app = dash.Dash(__name__)
app.title = "🚀 DA-KI Live-Monitoring - 5 Slots"

def get_monitoring_data():
    """Hole aktuelle Monitoring-Daten von der API"""
    try:
        response = requests.get("http://localhost:8003/api/monitoring/summary", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"stocks": [], "total_positions": 0}
    except Exception as e:
        print(f"API-Fehler: {e}")
        return {"stocks": [], "total_positions": 0}

def create_slot_visual(slot_number, stock_data=None):
    """Erstelle einzelnen Slot für Portfolio-Visualisierung"""
    
    if stock_data:
        # Belegter Slot
        profit_loss = stock_data.get('profit_loss', 0)
        change_percent = stock_data.get('change_percent', 0)
        profit_color = '#27ae60' if profit_loss >= 0 else '#e74c3c'
        
        return html.Div([
            html.H3(f"📈 {stock_data['symbol']}", 
                   style={'margin': '0 0 10px 0', 'color': 'white', 'fontSize': '18px'}),
            html.P(f"Investment: €{stock_data['investment_amount']:.0f}", 
                  style={'margin': '0 0 5px 0', 'color': 'white', 'fontSize': '12px'}),
            html.P(f"Aktuell: €{stock_data['total_value']:.0f}", 
                  style={'margin': '0 0 5px 0', 'color': 'white', 'fontSize': '12px'}),
            html.P(f"{stock_data['shares']} Aktien", 
                  style={'margin': '0 0 8px 0', 'color': 'white', 'fontSize': '11px'}),
            html.P(f"{change_percent:+.1f}% ({profit_loss:+.0f}€)", 
                  style={'margin': '0', 'color': 'white', 'fontSize': '12px', 'fontWeight': 'bold'})
        ], style={
            'backgroundColor': profit_color,
            'border': f'3px solid {profit_color}',
            'width': '18%',
            'height': '140px',
            'borderRadius': '15px',
            'display': 'inline-block',
            'margin': '1%',
            'padding': '15px',
            'textAlign': 'center',
            'verticalAlign': 'top',
            'boxShadow': '0 4px 8px rgba(0,0,0,0.1)'
        })
    else:
        # Freier Slot
        return html.Div([
            html.H3(f"Slot {slot_number}", 
                   style={'margin': '0 0 10px 0', 'color': '#7f8c8d', 'fontSize': '18px'}),
            html.P("FREI", 
                  style={'margin': '0 0 10px 0', 'color': '#7f8c8d', 'fontSize': '16px', 'fontWeight': 'bold'}),
            html.P("Verfügbar für", 
                  style={'margin': '0 0 5px 0', 'color': '#7f8c8d', 'fontSize': '10px'}),
            html.P("neue Position", 
                  style={'margin': '0', 'color': '#7f8c8d', 'fontSize': '10px'})
        ], style={
            'backgroundColor': '#ecf0f1',
            'border': '3px dashed #bdc3c7',
            'width': '18%',
            'height': '140px',
            'borderRadius': '15px',
            'display': 'inline-block',
            'margin': '1%',
            'padding': '15px',
            'textAlign': 'center',
            'verticalAlign': 'top'
        })

def create_portfolio_summary(api_data):
    """Erstelle Portfolio-Zusammenfassung"""
    total_investment = api_data.get('total_investment', 0)
    total_value = api_data.get('total_current_value', 0)
    total_profit = total_value - total_investment
    total_change = (total_profit / total_investment * 100) if total_investment > 0 else 0
    
    return html.Div([
        html.H2("📊 Live-Monitoring Portfolio", style={'color': '#2c3e50', 'marginBottom': 20, 'textAlign': 'center'}),
        html.Div([
            html.Div([
                html.H3(f"€{total_investment:.0f}", style={'margin': 0, 'color': '#3498db', 'fontSize': '24px'}),
                html.P("Gesamt Investment", style={'margin': 0, 'color': '#7f8c8d', 'fontSize': '12px'})
            ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px', 'margin': '10px', 'width': '30%', 'display': 'inline-block', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
            
            html.Div([
                html.H3(f"€{total_value:.0f}", style={'margin': 0, 'color': '#27ae60', 'fontSize': '24px'}),
                html.P("Aktueller Wert", style={'margin': 0, 'color': '#7f8c8d', 'fontSize': '12px'})
            ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px', 'margin': '10px', 'width': '30%', 'display': 'inline-block', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
            
            html.Div([
                html.H3(f"{total_change:+.1f}%", 
                       style={'margin': '0 0 5px 0', 'color': '#27ae60' if total_profit >= 0 else '#e74c3c', 'fontSize': '24px'}),
                html.P(f"({total_profit:+.0f}€)", 
                       style={'margin': 0, 'color': '#27ae60' if total_profit >= 0 else '#e74c3c', 'fontSize': '14px'}),
                html.P("Gewinn/Verlust", style={'margin': '5px 0 0 0', 'color': '#7f8c8d', 'fontSize': '12px'})
            ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px', 'margin': '10px', 'width': '30%', 'display': 'inline-block', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
        ], style={'textAlign': 'center'})
    ])

# Layout
app.layout = html.Div([
    html.Div([
        html.H1("🚀 DA-KI Live-Monitoring Dashboard", 
               style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 10}),
        html.H2("5 Aktienplätze Portfolio", 
               style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': 30, 'fontSize': '18px'})
    ]),
    
    # Auto-Update Interval
    dcc.Interval(
        id='interval-component',
        interval=15*1000,  # Update alle 15 Sekunden
        n_intervals=0
    ),
    
    # Portfolio Summary
    html.Div(id='portfolio-summary-live'),
    
    # 5-Slot Visualisierung
    html.Div([
        html.H2("🎯 Portfolio-Plätze (5 Slots)", 
               style={'color': '#2c3e50', 'marginBottom': 20, 'textAlign': 'center', 'fontSize': '22px'}),
        html.Div(id='portfolio-slots-live', style={
            'textAlign': 'center',
            'backgroundColor': '#f8f9fa',
            'padding': '25px',
            'borderRadius': '15px',
            'border': '2px solid #dee2e6',
            'boxShadow': '0 4px 8px rgba(0,0,0,0.1)'
        })
    ], style={'marginTop': 40}),
    
    # Status Info
    html.Div(id='status-info', style={'textAlign': 'center', 'marginTop': 30, 'padding': '15px'})
    
], style={'padding': '30px', 'maxWidth': '1400px', 'margin': '0 auto', 'backgroundColor': '#ffffff'})

@app.callback(
    [Output('portfolio-summary-live', 'children'),
     Output('portfolio-slots-live', 'children'),
     Output('status-info', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_portfolio_display(n):
    """Update Portfolio-Anzeige alle 15 Sekunden"""
    
    # Hole aktuelle API-Daten
    api_data = get_monitoring_data()
    
    # Erstelle Summary
    summary = create_portfolio_summary(api_data)
    
    # Erstelle 5 Slots
    stocks = api_data.get('stocks', [])
    slots = []
    
    for i in range(1, 6):
        if i <= len(stocks):
            # Belegter Slot
            stock_data = stocks[i-1]
            slot = create_slot_visual(i, stock_data)
        else:
            # Freier Slot
            slot = create_slot_visual(i)
        slots.append(slot)
    
    # Status Info
    now = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    occupied_slots = len(stocks)
    free_slots = 5 - occupied_slots
    
    status_info = html.Div([
        html.P(f"🔄 Letztes Update: {now}", 
               style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0 0 5px 0'}),
        html.P(f"📊 Portfolio Status: {occupied_slots}/5 Slots belegt • {free_slots} Slots frei", 
               style={'fontSize': '14px', 'color': '#2c3e50', 'fontWeight': 'bold', 'margin': 0}),
        html.P(f"🌐 Dashboard läuft auf: http://10.1.1.110:8054", 
               style={'fontSize': '11px', 'color': '#7f8c8d', 'margin': '5px 0 0 0'})
    ], style={'backgroundColor': '#f8f9fa', 'padding': '15px', 'borderRadius': '8px', 'border': '1px solid #dee2e6'})
    
    return summary, slots, status_info

if __name__ == '__main__':
    print("🚀 Starte FINALES Live-Monitoring Dashboard...")
    print("📊 URL: http://10.1.1.110:8054")
    print("⚠️  Verwendung AUSSCHLIESSLICH der IP 10.1.1.110 und Port 8054!")
    print("🔄 Auto-Update alle 15 Sekunden")
    print("🎯 5-Slot Portfolio Visualisierung mit Live-API-Daten")
    app.run(debug=False, host='0.0.0.0', port=8054)