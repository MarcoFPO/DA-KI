#!/usr/bin/env python3
"""
KI-Wachstumsprognose Module - Isolierte Komponente für Wachstumsprognose-Features
Definierte Schnittstellen für Datenaustausch mit dem Hauptdashboard
"""

from dash import html, dcc
import plotly.graph_objs as go
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional

class KIWachstumsprognoseModule:
    """Isolierte KI-Wachstumsprognose Komponente mit definierten Schnittstellen"""
    
    def __init__(self, api_base_url: str = "http://10.1.1.110:8003"):
        # VERBOTEN: Verwendung von Loopback-Adressen (127.0.0.1, localhost)
        self.api_base_url = api_base_url
        self.fallback_data = self._create_fallback_data()
        
    # ================== PUBLIC INTERFACES ==================
    
    def get_aktien_daten(self) -> List[Dict[str, Any]]:
        """
        SCHNITTSTELLE: Hole Aktien-Daten von API oder Fallback
        
        Output: Liste mit 10 Aktien-Datensätzen
        """
        try:
            response = requests.get(f"{self.api_base_url}/api/wachstumsprognose/top10", timeout=3)
            if response.status_code == 200:
                data = response.json()
                return data.get('top_10_wachstums_aktien', self.fallback_data)
        except:
            pass
        
        return self.fallback_data
    
    def create_karten_layout_5x2(self, aktien_daten: List[Dict]) -> html.Div:
        """
        SCHNITTSTELLE: Erstelle 5x2 Karten-Layout für KI-Wachstumsprognose
        
        Input: aktien_daten (List[Dict]) - Liste mit Aktien-Daten
        Output: html.Div - Fertiges 5x2 Grid Layout
        """
        if not aktien_daten:
            return self._create_empty_cards_layout()
        
        # Linke Spalte (Aktien 1-5)
        linke_spalte = self._create_cards_column(aktien_daten[:5])
        
        # Rechte Spalte (Aktien 6-10) 
        rechte_spalte = self._create_cards_column(aktien_daten[5:10])
        
        return html.Div([
            html.Div(linke_spalte, style={'gridColumn': '1'}),
            html.Div(rechte_spalte, style={'gridColumn': '2'})
        ], style={
            'display': 'grid',
            'gridTemplateColumns': '1fr 1fr',
            'gap': '20px',
            'width': '100%'
        })
    
    def create_wachstums_charts(self, aktien_daten: List[Dict]) -> tuple:
        """
        SCHNITTSTELLE: Erstelle Charts für Wachstums-Score und Rendite-Prognose
        
        Input: aktien_daten (List[Dict]) - Liste mit Aktien-Daten
        Output: tuple (ranking_chart, rendite_chart) - Zwei Chart-Dictionaries
        """
        if not aktien_daten:
            return self._create_empty_charts()
        
        symbols = [aktie['symbol'] for aktie in aktien_daten]
        scores = [aktie['wachstums_score'] for aktie in aktien_daten]
        renditen = [aktie.get('prognose_30_tage', {}).get('erwartete_rendite_prozent', 0) 
                   for aktie in aktien_daten]
        
        # Wachstums-Score Chart
        ranking_chart = {
            'data': [go.Bar(x=symbols, y=scores, marker_color='#e74c3c')],
            'layout': go.Layout(
                title='KI-Wachstums-Score TOP 10',
                xaxis={'title': 'Aktien'},
                yaxis={'title': 'Score'},
                height=300
            )
        }
        
        # Rendite-Prognose Chart
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
    
    def create_prognose_tabelle_basis(self, aktien_daten: List[Dict]) -> html.Table:
        """
        SCHNITTSTELLE: Erstelle Basis-Tabelle für detaillierte Prognose (ohne Action-Spalte)
        
        Input: aktien_daten (List[Dict]) - Liste mit Aktien-Daten
        Output: html.Table - Fertige Prognose-Tabelle (9 Spalten)
        """
        if not aktien_daten:
            return self._create_empty_table()
        
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
                html.Td(f"+{prognose.get('erwartete_rendite_prozent', 0):.1f}%", 
                        style={'color': '#27ae60'}),
                html.Td(prognose.get('vertrauen_level', 'N/A'))
            ])
            zeilen.append(zeile)
        
        return html.Table([
            html.Thead([
                html.Tr([
                    html.Th("Rang", style=self._get_header_style()),
                    html.Th("Aktie", style=self._get_header_style()),
                    html.Th("Branche", style=self._get_header_style()),
                    html.Th("WKN", style=self._get_header_style()),
                    html.Th("Kurs", style=self._get_header_style()),
                    html.Th("KI-Score", style=self._get_header_style()),
                    html.Th("30T Prognose", style=self._get_header_style()),
                    html.Th("Rendite", style=self._get_header_style()),
                    html.Th("Vertrauen", style=self._get_header_style())
                ])
            ]),
            html.Tbody(zeilen)
        ], style={'width': '100%', 'borderCollapse': 'collapse'})
    
    def create_wachstumsprognose_container(self, aktien_daten: List[Dict]) -> html.Div:
        """
        SCHNITTSTELLE: Erstelle vollständigen KI-Wachstumsprognose Container
        
        Input: aktien_daten (List[Dict]) - Liste mit Aktien-Daten
        Output: html.Div - Vollständiger Container mit Header und Inhalt
        """
        karten_layout = self.create_karten_layout_5x2(aktien_daten)
        
        return html.Div([
            html.H2("📈 KI-Wachstumsprognose (5x2 Layout)", 
                   style={'color': '#e74c3c', 'marginBottom': 20}),
            karten_layout
        ], style={
            'backgroundColor': '#fff5f5', 
            'padding': '20px', 
            'marginBottom': '20px',
            'borderRadius': '10px', 
            'border': '2px solid #e74c3c'
        })
    
    def create_charts_container(self, aktien_daten: List[Dict]) -> html.Div:
        """
        SCHNITTSTELLE: Erstelle Charts Container mit beiden Charts nebeneinander
        
        Input: aktien_daten (List[Dict]) - Liste mit Aktien-Daten
        Output: html.Div - Container mit Wachstums-Score und Rendite Charts
        """
        ranking_chart, rendite_chart = self.create_wachstums_charts(aktien_daten)
        
        return html.Div([
            html.Div([
                html.H3("📊 Wachstums-Score", style={'textAlign': 'center'}),
                dcc.Graph(figure=ranking_chart)
            ], style={'width': '48%', 'display': 'inline-block'}),
            
            html.Div([
                html.H3("📈 Rendite-Prognose", style={'textAlign': 'center'}),
                dcc.Graph(figure=rendite_chart)
            ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%'})
        ], style={'marginBottom': 20})
    
    def get_status_info(self, aktien_daten: List[Dict]) -> Dict[str, Any]:
        """
        SCHNITTSTELLE: Hole Status-Informationen für Dashboard-Updates
        
        Input: aktien_daten (List[Dict]) - Liste mit Aktien-Daten
        Output: Dict mit Status-Informationen
        """
        return {
            'anzahl_aktien': len(aktien_daten),
            'letztes_update': datetime.now().strftime('%H:%M:%S'),
            'avg_score': sum(aktie['wachstums_score'] for aktie in aktien_daten) / len(aktien_daten) if aktien_daten else 0,
            'top_performer': aktien_daten[0] if aktien_daten else None,
            'data_source': 'API' if self._is_api_data(aktien_daten) else 'Fallback'
        }
    
    # ================== PRIVATE HELPERS ==================
    
    def _create_fallback_data(self) -> List[Dict]:
        """Private: Erstelle Fallback Mock-Daten"""
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
    
    def _create_cards_column(self, aktien_subset: List[Dict]) -> List[html.Div]:
        """Private: Erstelle Karten für eine Spalte"""
        karten = []
        for aktie in aktien_subset:
            prognose = aktie.get('prognose_30_tage', {})
            karte = html.Div([
                html.H4(f"#{aktie['rank']}", 
                       style={'position': 'absolute', 'top': '5px', 'left': '5px', 'color': '#e74c3c'}),
                html.H4(aktie['symbol'], 
                       style={'textAlign': 'center', 'marginBottom': 10}),
                html.P(aktie['name'][:25], 
                      style={'textAlign': 'center', 'fontSize': '12px', 'color': '#7f8c8d'}),
                html.P(f"🏢 {aktie['branche']}", style={'fontSize': '11px'}),
                html.P(f"🏷️ {aktie['wkn']}", style={'fontSize': '10px', 'color': '#7f8c8d'}),
                html.H3(f"€{aktie['current_price']}", 
                       style={'textAlign': 'center', 'color': '#27ae60'}),
                html.P(f"KI-Score: {aktie['wachstums_score']}/100", 
                      style={'fontWeight': 'bold', 'color': '#e74c3c'}),
                html.P(f"Rendite: +{prognose.get('erwartete_rendite_prozent', 0):.1f}%", 
                      style={'color': '#27ae60'})
            ], style={
                'padding': '15px', 'margin': '10px 0', 'backgroundColor': 'white',
                'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
                'position': 'relative', 'minHeight': '280px'
            })
            karten.append(karte)
        return karten
    
    def _create_empty_cards_layout(self) -> html.Div:
        """Private: Erstelle leeres Karten-Layout"""
        return html.Div("Keine Daten verfügbar", 
                       style={'textAlign': 'center', 'padding': '40px'})
    
    def _create_empty_charts(self) -> tuple:
        """Private: Erstelle leere Charts"""
        empty_chart = {
            'data': [],
            'layout': {'title': 'Keine Daten verfügbar', 'height': 300}
        }
        return empty_chart, empty_chart
    
    def _create_empty_table(self) -> html.Div:
        """Private: Erstelle leere Tabelle"""
        return html.Div("Keine Daten verfügbar", 
                       style={'textAlign': 'center', 'padding': '40px'})
    
    def _get_header_style(self) -> Dict:
        """Private: Standard Header-Style für Tabellen"""
        return {
            'padding': '10px', 
            'backgroundColor': '#e74c3c', 
            'color': 'white'
        }
    
    def _is_api_data(self, aktien_daten: List[Dict]) -> bool:
        """Private: Prüfe ob Daten von API oder Fallback"""
        return aktien_daten != self.fallback_data

# ================== DATENINTERFACE ==================

class WachstumsprognoseDataInterface:
    """Definierte Schnittstelle für Datenaustausch mit anderen Modulen"""
    
    @staticmethod
    def extract_aktie_by_symbol(aktien_list: List[Dict], symbol: str) -> Optional[Dict]:
        """
        Extrahiere Aktien-Daten für spezifisches Symbol
        
        Input: aktien_list, symbol
        Output: Aktien-Daten oder None
        """
        try:
            for aktie in aktien_list:
                if aktie.get('symbol') == symbol:
                    return aktie
            return None
        except:
            return None
    
    @staticmethod
    def format_aktie_for_external_use(aktie_data: Dict) -> Dict:
        """
        Formatiere Aktien-Daten für externen Gebrauch (z.B. Live-Monitoring)
        
        Input: aktie_data
        Output: Standardisierte Aktien-Daten
        """
        if not aktie_data:
            return {}
        
        return {
            'symbol': aktie_data.get('symbol', ''),
            'name': aktie_data.get('name', ''),
            'current_price': aktie_data.get('current_price', 0),
            'wachstums_score': aktie_data.get('wachstums_score', 0),
            'rank': aktie_data.get('rank', 0),
            'branche': aktie_data.get('branche', ''),
            'wkn': aktie_data.get('wkn', ''),
            'prognose_30_tage': aktie_data.get('prognose_30_tage', {})
        }
    
    @staticmethod
    def get_top_performers(aktien_list: List[Dict], count: int = 3) -> List[Dict]:
        """
        Hole Top-Performer basierend auf Wachstums-Score
        
        Input: aktien_list, count
        Output: Liste der Top-Performer
        """
        try:
            sorted_aktien = sorted(aktien_list, 
                                 key=lambda x: x.get('wachstums_score', 0), 
                                 reverse=True)
            return sorted_aktien[:count]
        except:
            return []
    
    @staticmethod
    def calculate_portfolio_metrics(aktien_list: List[Dict]) -> Dict:
        """
        Berechne Portfolio-Metriken für Wachstumsprognose
        
        Input: aktien_list
        Output: Dict mit Metriken
        """
        if not aktien_list:
            return {
                'total_stocks': 0,
                'avg_wachstums_score': 0,
                'avg_rendite': 0,
                'total_market_value': 0
            }
        
        avg_score = sum(aktie.get('wachstums_score', 0) for aktie in aktien_list) / len(aktien_list)
        avg_rendite = sum(aktie.get('prognose_30_tage', {}).get('erwartete_rendite_prozent', 0) 
                         for aktie in aktien_list) / len(aktien_list)
        total_value = sum(aktie.get('current_price', 0) for aktie in aktien_list)
        
        return {
            'total_stocks': len(aktien_list),
            'avg_wachstums_score': round(avg_score, 1),
            'avg_rendite': round(avg_rendite, 1),
            'total_market_value': round(total_value, 2)
        }

# ================== EXPORT ==================

def create_wachstumsprognose_instance(api_base_url: str = "http://10.1.1.110:8003"):
    """Factory-Funktion für KI-Wachstumsprognose-Instanz"""
    return KIWachstumsprognoseModule(api_base_url)

def get_wachstumsprognose_data_interface():
    """Factory-Funktion für Wachstumsprognose-Daten-Interface"""
    return WachstumsprognoseDataInterface()

# ================== CALLBACK HELPERS ==================

def get_wachstumsprognose_callback_pattern():
    """
    Definiere Callback-Pattern für Wachstumsprognose-Updates
    Wird vom Hauptdashboard verwendet
    """
    return {
        'update_inputs': ['refresh-btn'],
        'update_outputs': [
            'aktien-karten',
            'ranking-chart', 
            'rendite-chart',
            'prognose-tabelle-basis'
        ],
        'status_outputs': ['wachstumsprognose-status']
    }