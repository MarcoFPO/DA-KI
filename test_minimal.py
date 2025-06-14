#!/usr/bin/env python3
"""
MINIMAL Dash Test - um das Loading-Problem zu identifizieren
"""

import dash
from dash import html

# Minimal App
app = dash.Dash(__name__)

# Minimal Layout
app.layout = html.Div([
    html.H1("TEST"),
    html.P("Hello World")
])

if __name__ == '__main__':
    print("🧪 Testing minimal Dash app...")
    app.run(debug=True, host='::', port=8054)