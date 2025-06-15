#!/usr/bin/env python3
"""
Frontend Layout Module - Isolierte Layout-Komponenten
Definierte Schnittstellen für Header, Navigation und Container
"""

from dash import html
from datetime import datetime
from typing import Dict, List, Any, Optional

class FrontendLayoutModule:
    """Isoliertes Frontend-Layout-Modul mit definierten Schnittstellen"""
    
    def __init__(self, app_title: str = "🚀 DA-KI Dashboard"):
        self.app_title = app_title
        self.base_styles = self._create_base_styles()
        
    # ================== PUBLIC LAYOUT INTERFACES ==================
    
    def create_main_header(self, subtitle: str = "Modulare Architektur • KI-Wachstumsprognose mit Live-Monitoring") -> html.Div:
        """
        SCHNITTSTELLE: Erstelle Haupt-Header für Dashboard
        
        Input: subtitle (str) - Untertitel des Dashboards
        Output: html.Div - Header-Container
        """
        return html.Div([
            html.H1(self.app_title, 
                    style=self.base_styles['main_title']),
            html.P(subtitle, 
                   style=self.base_styles['subtitle'])
        ], style=self.base_styles['header_container'])
    
    def create_action_bar(self, refresh_button_text: str = "🔄 Daten aktualisieren") -> html.Div:
        """
        SCHNITTSTELLE: Erstelle Action-Bar mit Refresh-Button
        
        Input: refresh_button_text (str) - Text für Refresh-Button
        Output: html.Div - Action-Bar Container
        """
        return html.Div([
            html.Button(refresh_button_text, 
                       id='refresh-btn',
                       style=self.base_styles['refresh_button'])
        ], style=self.base_styles['action_bar'])
    
    def create_status_container(self) -> html.Div:
        """
        SCHNITTSTELLE: Erstelle Status-Nachrichten Container
        
        Output: html.Div - Status Container mit Message-Bereichen
        """
        return html.Div([
            html.Div(id='status-message', style=self.base_styles['status_area']),
            html.Div(id='action-message', style=self.base_styles['status_area'])
        ])
    
    def create_section_container(self, title: str, content: Any, 
                               background_color: str = "#ffffff", 
                               border_color: str = "#e74c3c") -> html.Div:
        """
        SCHNITTSTELLE: Erstelle Section-Container mit Titel und Inhalt
        
        Input: 
            title (str) - Section-Titel
            content (Any) - Section-Inhalt
            background_color (str) - Hintergrundfarbe
            border_color (str) - Rahmenfarbe
        Output: html.Div - Section-Container
        """
        container_style = self.base_styles['section_container'].copy()
        container_style.update({
            'backgroundColor': background_color,
            'border': f'2px solid {border_color}'
        })
        
        return html.Div([
            html.H3(title, style=self.base_styles['section_title']),
            html.Div(content if content is not None else "Inhalt wird geladen...",
                     style=self.base_styles['section_content'])
        ], style=container_style)
    
    def create_two_column_layout(self, left_content: Any, right_content: Any) -> html.Div:
        """
        SCHNITTSTELLE: Erstelle zweispaltiges Layout
        
        Input: 
            left_content (Any) - Inhalt linke Spalte
            right_content (Any) - Inhalt rechte Spalte  
        Output: html.Div - Zweispaltiger Container
        """
        return html.Div([
            html.Div(left_content, style=self.base_styles['column_left']),
            html.Div(right_content, style=self.base_styles['column_right'])
        ], style=self.base_styles['two_column_container'])
    
    def create_footer(self) -> html.Div:
        """
        SCHNITTSTELLE: Erstelle Footer mit Zeitstempel
        
        Output: html.Div - Footer-Container
        """
        timestamp = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        return html.Div([
            html.P(f"🤖 Modulares DA-KI Dashboard | 🕒 {timestamp} | 🔧 Frontend modular isoliert",
                   style=self.base_styles['footer_text'])
        ], style=self.base_styles['footer_container'])
    
    def create_main_layout_container(self, children: List[Any]) -> html.Div:
        """
        SCHNITTSTELLE: Erstelle Haupt-Layout-Container
        
        Input: children (List[Any]) - Liste von Layout-Elementen
        Output: html.Div - Haupt-Container
        """
        return html.Div(children, style=self.base_styles['main_container'])
    
    # ================== PRIVATE STYLE DEFINITIONS ==================
    
    def _create_base_styles(self) -> Dict[str, Dict]:
        """Private: Definiere Basis-Styles für Layout-Komponenten"""
        return {
            'main_container': {
                'margin': '20px',
                'fontFamily': 'Arial, sans-serif'
            },
            'header_container': {
                'textAlign': 'center',
                'marginBottom': '30px'
            },
            'main_title': {
                'textAlign': 'center', 
                'color': '#2c3e50', 
                'marginBottom': '10px',
                'fontSize': '32px'
            },
            'subtitle': {
                'textAlign': 'center', 
                'color': '#7f8c8d', 
                'marginBottom': '30px',
                'fontSize': '16px'
            },
            'action_bar': {
                'textAlign': 'center',
                'marginBottom': '20px'
            },
            'refresh_button': {
                'padding': '10px 20px', 
                'backgroundColor': '#3498db', 
                'color': 'white',
                'border': 'none', 
                'borderRadius': '5px',
                'cursor': 'pointer',
                'fontSize': '14px'
            },
            'status_area': {
                'marginBottom': '20px'
            },
            'section_container': {
                'padding': '20px', 
                'marginBottom': '20px',
                'borderRadius': '10px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            },
            'section_title': {
                'color': '#2c3e50',
                'marginBottom': '15px',
                'fontSize': '20px'
            },
            'section_content': {
                'minHeight': '50px'
            },
            'two_column_container': {
                'display': 'flex',
                'gap': '20px',
                'marginBottom': '20px'
            },
            'column_left': {
                'flex': '1'
            },
            'column_right': {
                'flex': '1'
            },
            'footer_container': {
                'textAlign': 'center',
                'marginTop': '30px',
                'paddingTop': '20px',
                'borderTop': '1px solid #ecf0f1'
            },
            'footer_text': {
                'color': '#95a5a6',
                'fontSize': '12px',
                'margin': '0'
            }
        }

# ================== LAYOUT DATA INTERFACE ==================

class LayoutDataInterface:
    """Definierte Schnittstelle für Layout-Daten"""
    
    @staticmethod
    def format_status_message(message: str, message_type: str = "info") -> html.Div:
        """
        Formatiere Status-Nachricht mit Typ-spezifischem Styling
        
        Input: 
            message (str) - Nachrichtentext
            message_type (str) - 'success', 'error', 'warning', 'info'
        Output: html.Div - Formatierte Nachricht
        """
        style_map = {
            'success': {'color': '#27ae60', 'backgroundColor': '#d4edda'},
            'error': {'color': '#e74c3c', 'backgroundColor': '#f8d7da'},
            'warning': {'color': '#f39c12', 'backgroundColor': '#fff3cd'},
            'info': {'color': '#3498db', 'backgroundColor': '#d1ecf1'}
        }
        
        style = style_map.get(message_type, style_map['info'])
        style.update({
            'padding': '10px',
            'borderRadius': '5px',
            'fontWeight': 'bold'
        })
        
        return html.Div([
            html.Span(message, style=style)
        ])
    
    @staticmethod
    def create_loading_placeholder(text: str = "Daten werden geladen...") -> html.Div:
        """
        Erstelle Loading-Placeholder für Komponenten
        
        Input: text (str) - Loading-Text
        Output: html.Div - Loading-Placeholder
        """
        return html.Div([
            html.P(text, style={
                'textAlign': 'center',
                'color': '#7f8c8d',
                'fontStyle': 'italic',
                'padding': '40px'
            })
        ])
    
    @staticmethod
    def validate_component_props(component: Any, required_props: List[str]) -> bool:
        """
        Validiere ob Komponente alle erforderlichen Properties hat
        
        Input:
            component (Any) - Zu validierende Komponente
            required_props (List[str]) - Liste erforderlicher Properties
        Output: bool - Validation erfolgreich
        """
        if not hasattr(component, 'children'):
            return False
        
        for prop in required_props:
            if not hasattr(component, prop):
                return False
                
        return True

# ================== EXPORT ==================

def create_frontend_layout_instance(app_title: str = "🚀 DA-KI Dashboard"):
    """Factory-Funktion für Frontend-Layout-Instanz"""
    return FrontendLayoutModule(app_title)

def get_layout_data_interface():
    """Factory-Funktion für Layout-Daten-Interface"""
    return LayoutDataInterface()

# ================== STYLE CONSTANTS ==================

SECTION_STYLES = {
    'wachstumsprognose': {
        'background_color': '#fff5f5',
        'border_color': '#e74c3c'
    },
    'live_monitoring': {
        'background_color': '#f0f8ff', 
        'border_color': '#3498db'
    },
    'charts': {
        'background_color': '#f8f9fa',
        'border_color': '#6c757d'
    }
}