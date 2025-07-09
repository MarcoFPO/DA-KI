#!/usr/bin/env python3
"""
Einfaches 5-Slot Live-Monitoring Dashboard
Direkte Implementierung ohne komplexe Module
"""

import dash
from dash import html, dcc, Input, Output, callback
import requests
import json
from datetime import datetime

app = dash.Dash(__name__)
app.title = "🚀 Live-Monitoring 5-Slot Dashboard"

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
            html.H4(f"📈 {stock_data['symbol']}", 
                   style={'margin': '0 0 8px 0', 'color': 'white', 'fontSize': '16px'}),
            html.P(f"€{stock_data['investment_amount']:.0f} → €{stock_data['total_value']:.0f}", 
                  style={'margin': '0 0 4px 0', 'color': 'white', 'fontSize': '11px'}),
            html.P(f"{stock_data['shares']} Aktien", 
                  style={'margin': '0 0 4px 0', 'color': 'white', 'fontSize': '10px'}),
            html.P(f"{change_percent:+.1f}% ({profit_loss:+.0f}€)", 
                  style={'margin': '0', 'color': 'white', 'fontSize': '10px', 'fontWeight': 'bold'})
        ], style={
            'backgroundColor': profit_color,
            'border': f'2px solid {profit_color}',
            'width': '18%',
            'height': '120px',
            'borderRadius': '12px',
            'display': 'inline-block',
            'margin': '1%',
            'padding': '12px',
            'textAlign': 'center',
            'verticalAlign': 'top'
        })
    else:
        # Freier Slot
        return html.Div([
            html.H4(f"Platz {slot_number}", 
                   style={'margin': '0 0 8px 0', 'color': '#7f8c8d', 'fontSize': '16px'}),
            html.P("FREI", 
                  style={'margin': '0', 'color': '#7f8c8d', 'fontSize': '14px', 'fontWeight': 'bold'}),
            html.P("Verfügbar für neue Position", 
                  style={'margin': '10px 0 0 0', 'color': '#7f8c8d', 'fontSize': '9px'})
        ], style={
            'backgroundColor': '#ecf0f1',
            'border': '2px dashed #bdc3c7',
            'width': '18%',
            'height': '120px',
            'borderRadius': '12px',
            'display': 'inline-block',
            'margin': '1%',
            'padding': '12px',
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
        html.H3("📊 Portfolio-Übersicht", style={'color': '#2c3e50', 'marginBottom': 15}),
        html.Div([
            html.Div([
                html.H4(f"€{total_investment:.0f}", style={'margin': 0, 'color': '#3498db'}),
                html.P("Investment", style={'margin': 0, 'color': '#7f8c8d'})
            ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px', 'margin': '5px', 'width': '30%', 'display': 'inline-block'}),
            
            html.Div([
                html.H4(f"€{total_value:.0f}", style={'margin': 0, 'color': '#27ae60'}),
                html.P("Aktueller Wert", style={'margin': 0, 'color': '#7f8c8d'})
            ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px', 'margin': '5px', 'width': '30%', 'display': 'inline-block'}),
            
            html.Div([
                html.H4(f"{total_change:+.1f}% ({total_profit:+.0f}€)", 
                       style={'margin': 0, 'color': '#27ae60' if total_profit >= 0 else '#e74c3c'}),
                html.P("Gewinn/Verlust", style={'margin': 0, 'color': '#7f8c8d'})
            ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px', 'margin': '5px', 'width': '30%', 'display': 'inline-block'})
        ])
    ])

# Layout
app.layout = html.Div([
    html.H1("🚀 Live-Monitoring Dashboard - 5 Aktienplätze", 
           style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
    
    # Auto-Update Interval
    dcc.Interval(
        id='interval-component',
        interval=10*1000,  # Update alle 10 Sekunden
        n_intervals=0
    ),
    
    # Portfolio Summary
    html.Div(id='portfolio-summary-live'),
    
    # 5-Slot Visualisierung
    html.Div([
        html.H3("🎯 Portfolio-Plätze (5 Slots)", style={'color': '#2c3e50', 'marginBottom': 15, 'textAlign': 'center'}),
        html.Div(id='portfolio-slots-live', style={
            'textAlign': 'center',
            'backgroundColor': '#f8f9fa',
            'padding': '20px',
            'borderRadius': '10px',
            'border': '1px solid #dee2e6'
        })
    ], style={'marginTop': 30}),
    
    # Last Update Info
    html.Div(id='last-update-info', style={'textAlign': 'center', 'marginTop': 20, 'color': '#7f8c8d'})
    
], style={'padding': '20px', 'maxWidth': '1200px', 'margin': '0 auto'})

@app.callback(
    [Output('portfolio-summary-live', 'children'),
     Output('portfolio-slots-live', 'children'),
     Output('last-update-info', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_portfolio_display(n):
    """Update Portfolio-Anzeige alle 10 Sekunden"""
    
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
    
    # Last Update Info
    now = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    update_info = html.P(f"🔄 Letztes Update: {now} | Positionen: {len(stocks)}/5", 
                        style={'fontSize': '12px'})
    
    return summary, slots, update_info

if __name__ == '__main__':
    print("🚀 Starte Live-Monitoring 5-Slot Dashboard...")
    print("📊 URL: http://localhost:8060")
    print("🔄 Auto-Update alle 10 Sekunden")
    app.run(debug=False, host='0.0.0.0', port=8060)