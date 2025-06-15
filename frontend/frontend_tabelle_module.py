#!/usr/bin/env python3
"""
Frontend Tabelle Module - Isolierte Tabellen-Komponenten
Definierte Schnittstellen für Wachstumsprognose-Tabelle mit Action-Buttons
"""

from dash import html
from typing import Dict, List, Any, Optional

class FrontendTabelleModule:
    """Isoliertes Frontend-Tabellen-Modul mit Action-Button Integration"""
    
    def __init__(self):
        self.table_styles = self._create_table_styles()
        self.action_button_interface = None  # Wird durch Dependency Injection gesetzt
        
    # ================== PUBLIC TABLE INTERFACES ==================
    
    def set_action_button_interface(self, action_interface):
        """
        SCHNITTSTELLE: Setze Action-Button Interface (Dependency Injection)
        
        Input: action_interface - Interface für Action-Button Erstellung
        """
        self.action_button_interface = action_interface
    
    def create_wachstumsprognose_tabelle_mit_actions(self, aktien_daten: List[Dict]) -> html.Table:
        """
        SCHNITTSTELLE: Erstelle Wachstumsprognose-Tabelle mit Action-Buttons
        
        Input: aktien_daten (List[Dict]) - Liste mit Aktien-Daten
        Output: html.Table - Vollständige Tabelle mit Action-Spalte
        """
        if not aktien_daten:
            return self._create_empty_table()
        
        # Header erstellen
        header = self._create_table_header_with_actions()
        
        # Zeilen erstellen
        zeilen = []
        for i, aktie in enumerate(aktien_daten):
            zeile = self._create_table_row_with_action(aktie, i)
            zeilen.append(zeile)
        
        # Vollständige Tabelle
        return html.Table([
            html.Thead([header]),
            html.Tbody(zeilen)
        ], style=self.table_styles['main_table'])
    
    def create_basis_wachstumsprognose_tabelle(self, aktien_daten: List[Dict]) -> html.Table:
        """
        SCHNITTSTELLE: Erstelle Basis-Wachstumsprognose-Tabelle ohne Action-Buttons
        
        Input: aktien_daten (List[Dict]) - Liste mit Aktien-Daten  
        Output: html.Table - Basis-Tabelle ohne Action-Spalte
        """
        if not aktien_daten:
            return self._create_empty_table()
        
        # Header ohne Action-Spalte
        header = self._create_table_header_basis()
        
        # Zeilen ohne Action-Spalte
        zeilen = []
        for aktie in aktien_daten:
            zeile = self._create_table_row_basis(aktie)
            zeilen.append(zeile)
        
        return html.Table([
            html.Thead([header]),
            html.Tbody(zeilen)
        ], style=self.table_styles['main_table'])
    
    def create_table_container(self, table_content: Any, title: str) -> html.Div:
        """
        SCHNITTSTELLE: Erstelle Tabellen-Container mit Titel
        
        Input:
            table_content (Any) - Tabellen-Inhalt
            title (str) - Tabellen-Titel
        Output: html.Div - Container mit Titel und Tabelle
        """
        return html.Div([
            html.H3(title, style=self.table_styles['table_title']),
            html.Div(table_content, style=self.table_styles['table_wrapper'])
        ], style=self.table_styles['table_container'])
    
    # ================== PRIVATE TABLE CREATION ==================
    
    def _create_table_header_with_actions(self) -> html.Tr:
        """Private: Erstelle Tabellen-Header mit Action-Spalte"""
        header_style = self.table_styles['header_cell']
        
        return html.Tr([
            html.Th("Rang", style=header_style),
            html.Th("Aktie", style=header_style),
            html.Th("Branche", style=header_style),
            html.Th("WKN", style=header_style),
            html.Th("Kurs", style=header_style),
            html.Th("KI-Score", style=header_style),
            html.Th("30T Prognose", style=header_style),
            html.Th("Rendite", style=header_style),
            html.Th("Vertrauen", style=header_style),
            html.Th("🎯 Aktion", style=header_style)  # ACTION-SPALTE
        ])
    
    def _create_table_header_basis(self) -> html.Tr:
        """Private: Erstelle Basis-Tabellen-Header ohne Action-Spalte"""
        header_style = self.table_styles['header_cell']
        
        return html.Tr([
            html.Th("Rang", style=header_style),
            html.Th("Aktie", style=header_style),
            html.Th("Branche", style=header_style),
            html.Th("WKN", style=header_style),
            html.Th("Kurs", style=header_style),
            html.Th("KI-Score", style=header_style),
            html.Th("30T Prognose", style=header_style),
            html.Th("Rendite", style=header_style),
            html.Th("Vertrauen", style=header_style)
        ])
    
    def _create_table_row_with_action(self, aktie: Dict, index: int) -> html.Tr:
        """Private: Erstelle Tabellenzeile mit Action-Button"""
        prognose = aktie.get('prognose_30_tage', {})
        
        # Basis-Zellen
        basis_zellen = self._create_basis_cells(aktie, prognose)
        
        # Action-Button über Interface hinzufügen
        if self.action_button_interface:
            action_cell = self.action_button_interface.create_action_column_button(aktie, index)
            basis_zellen.append(action_cell)
        else:
            # Fallback wenn kein Action-Interface gesetzt
            action_cell = html.Td("N/A", style=self.table_styles['data_cell'])
            basis_zellen.append(action_cell)
        
        return html.Tr(basis_zellen)
    
    def _create_table_row_basis(self, aktie: Dict) -> html.Tr:
        """Private: Erstelle Basis-Tabellenzeile ohne Action-Button"""
        prognose = aktie.get('prognose_30_tage', {})
        basis_zellen = self._create_basis_cells(aktie, prognose)
        return html.Tr(basis_zellen)
    
    def _create_basis_cells(self, aktie: Dict, prognose: Dict) -> List[html.Td]:
        """Private: Erstelle Basis-Zellen für Tabellenzeile"""
        cell_style = self.table_styles['data_cell']
        
        return [
            html.Td(f"#{aktie.get('rank', 0)}", style={**cell_style, 'fontWeight': 'bold'}),
            html.Td(aktie.get('symbol', ''), style=cell_style),
            html.Td(aktie.get('branche', ''), style=cell_style),
            html.Td(aktie.get('wkn', ''), style=cell_style),
            html.Td(f"€{aktie.get('current_price', 0):.2f}", style=cell_style),
            html.Td(f"{aktie.get('wachstums_score', 0)}/100", style=cell_style),
            html.Td(f"€{prognose.get('prognostizierter_preis', 0):.2f}", style=cell_style),
            html.Td(f"+{prognose.get('erwartete_rendite_prozent', 0):.1f}%", 
                    style={**cell_style, 'color': '#27ae60'}),
            html.Td(prognose.get('vertrauen_level', 'N/A'), style=cell_style)
        ]
    
    def _create_empty_table(self) -> html.Div:
        """Private: Erstelle leere Tabelle-Placeholder"""
        return html.Div([
            html.P("Keine Daten verfügbar", 
                   style={'textAlign': 'center', 'padding': '40px', 'color': '#7f8c8d'})
        ])
    
    def _create_table_styles(self) -> Dict[str, Dict]:
        """Private: Definiere Tabellen-Styles"""
        return {
            'main_table': {
                'width': '100%',
                'borderCollapse': 'collapse',
                'backgroundColor': 'white',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            },
            'table_container': {
                'backgroundColor': 'white',
                'padding': '20px',
                'borderRadius': '10px',
                'marginBottom': '20px',
                'border': '1px solid #e9ecef'
            },
            'table_title': {
                'color': '#2c3e50',
                'marginBottom': '15px',
                'fontSize': '18px'
            },
            'table_wrapper': {
                'overflowX': 'auto'
            },
            'header_cell': {
                'padding': '12px',
                'backgroundColor': '#e74c3c',
                'color': 'white',
                'textAlign': 'left',
                'fontWeight': 'bold',
                'borderBottom': '2px solid #c0392b'
            },
            'data_cell': {
                'padding': '10px',
                'borderBottom': '1px solid #e9ecef',
                'textAlign': 'left'
            }
        }

# ================== TABLE DATA INTERFACE ==================

class TabelleDataInterface:
    """Definierte Schnittstelle für Tabellen-Daten"""
    
    @staticmethod
    def validate_aktien_data_structure(aktien_daten: List[Dict]) -> Dict[str, Any]:
        """
        Validiere Aktien-Datenstruktur für Tabelle
        
        Input: aktien_daten (List[Dict]) - Zu validierende Aktien-Daten
        Output: Dict mit Validierungsergebnis
        """
        if not aktien_daten:
            return {'valid': False, 'error': 'Keine Daten vorhanden'}
        
        required_fields = ['symbol', 'rank', 'branche', 'wkn', 'current_price', 'wachstums_score']
        missing_fields = []
        
        for i, aktie in enumerate(aktien_daten):
            for field in required_fields:
                if field not in aktie:
                    missing_fields.append(f"Aktie {i+1}: {field}")
        
        if missing_fields:
            return {
                'valid': False, 
                'error': f"Fehlende Felder: {', '.join(missing_fields[:5])}"
            }
        
        return {
            'valid': True,
            'count': len(aktien_daten),
            'first_symbol': aktien_daten[0].get('symbol', ''),
            'data_quality': 'OK'
        }
    
    @staticmethod
    def format_table_data_for_export(aktien_daten: List[Dict]) -> List[Dict]:
        """
        Formatiere Tabellen-Daten für Export/externe Nutzung
        
        Input: aktien_daten (List[Dict]) - Original Aktien-Daten
        Output: List[Dict] - Formatierte Daten
        """
        formatted_data = []
        
        for aktie in aktien_daten:
            prognose = aktie.get('prognose_30_tage', {})
            
            formatted_aktie = {
                'rang': aktie.get('rank', 0),
                'symbol': aktie.get('symbol', ''),
                'branche': aktie.get('branche', ''),
                'wkn': aktie.get('wkn', ''),
                'aktueller_kurs': aktie.get('current_price', 0),
                'ki_score': aktie.get('wachstums_score', 0),
                'prognose_preis': prognose.get('prognostizierter_preis', 0),
                'erwartete_rendite': prognose.get('erwartete_rendite_prozent', 0),
                'vertrauen': prognose.get('vertrauen_level', 'N/A')
            }
            formatted_data.append(formatted_aktie)
        
        return formatted_data
    
    @staticmethod
    def get_table_summary_stats(aktien_daten: List[Dict]) -> Dict[str, Any]:
        """
        Berechne Zusammenfassungs-Statistiken für Tabelle
        
        Input: aktien_daten (List[Dict]) - Aktien-Daten
        Output: Dict mit Statistiken
        """
        if not aktien_daten:
            return {'count': 0, 'avg_score': 0, 'avg_rendite': 0}
        
        scores = [aktie.get('wachstums_score', 0) for aktie in aktien_daten]
        renditen = [aktie.get('prognose_30_tage', {}).get('erwartete_rendite_prozent', 0) 
                   for aktie in aktien_daten]
        
        return {
            'count': len(aktien_daten),
            'avg_score': sum(scores) / len(scores) if scores else 0,
            'max_score': max(scores) if scores else 0,
            'min_score': min(scores) if scores else 0,
            'avg_rendite': sum(renditen) / len(renditen) if renditen else 0,
            'max_rendite': max(renditen) if renditen else 0,
            'top_performer': aktien_daten[0].get('symbol', '') if aktien_daten else ''
        }

# ================== EXPORT ==================

def create_frontend_tabelle_instance():
    """Factory-Funktion für Frontend-Tabelle-Instanz"""
    return FrontendTabelleModule()

def get_tabelle_data_interface():
    """Factory-Funktion für Tabelle-Daten-Interface"""
    return TabelleDataInterface()

# ================== ACTION BUTTON INTEGRATION ==================

class ActionButtonIntegration:
    """Integration-Klasse für Action-Button Module"""
    
    def __init__(self, live_monitoring_module):
        self.live_monitoring = live_monitoring_module
    
    def create_action_column_button(self, aktie: Dict, index: int):
        """Delegiere Action-Button Erstellung an Live-Monitoring Modul"""
        return self.live_monitoring.create_action_column_button(aktie, index)

def create_action_button_integration(live_monitoring_module):
    """Factory für Action-Button Integration"""
    return ActionButtonIntegration(live_monitoring_module)