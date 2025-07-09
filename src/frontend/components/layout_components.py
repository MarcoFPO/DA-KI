#!/usr/bin/env python3
"""
Layout Components - Wiederverwendbare UI-Komponenten
Migriert für neue Plugin-Architektur
"""

from dash import html, dcc
from datetime import datetime
from typing import Dict, List, Any, Optional

class LayoutComponents:
    """Sammlung wiederverwendbarer Layout-Komponenten"""
    
    def __init__(self):
        self.brand_colors = {
            'primary': '#3498db',
            'success': '#27ae60', 
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'info': '#17a2b8',
            'dark': '#2c3e50',
            'light': '#f8f9fa'
        }
    
    def create_main_header(self) -> html.Div:
        """Erstelle Haupt-Header"""
        return html.Div([
            html.Div([
                html.H1([
                    html.I(className="fas fa-chart-line", style={'marginRight': '10px'}),
                    "DA-KI Portfolio Management"
                ], style={
                    'margin': 0, 
                    'color': 'white',
                    'fontSize': '28px'
                }),
                html.P("Automatisierte Aktienanalyse mit KI-Integration", 
                      style={'margin': 0, 'color': '#ecf0f1', 'fontSize': '14px'})
            ], style={'flex': 1}),
            
            html.Div([
                html.Div(id='user-info-display', style={'color': 'white', 'textAlign': 'right'}),
                html.Button(
                    [html.I(className="fas fa-user"), " Login"],
                    id='login-btn',
                    style={
                        'backgroundColor': '#27ae60',
                        'color': 'white',
                        'border': 'none',
                        'padding': '8px 16px',
                        'borderRadius': '4px',
                        'marginTop': '10px'
                    }
                )
            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'flex-end'})
            
        ], style={
            'backgroundColor': self.brand_colors['dark'],
            'padding': '20px',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'space-between',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        })
    
    def create_navigation_bar(self) -> html.Div:
        """Erstelle Navigation Bar"""
        return html.Div([
            html.Div([
                html.Button([
                    html.I(className="fas fa-robot"), " KI-Analyse"
                ], id='nav-ki-btn', className='nav-btn'),
                
                html.Button([
                    html.I(className="fas fa-chart-bar"), " Live-Monitoring"
                ], id='nav-monitoring-btn', className='nav-btn'),
                
                html.Button([
                    html.I(className="fas fa-wallet"), " Portfolio"
                ], id='nav-portfolio-btn', className='nav-btn'),
                
                html.Button([
                    html.I(className="fas fa-plug"), " Plugins"
                ], id='nav-plugins-btn', className='nav-btn')
            ], style={
                'display': 'flex',
                'gap': '10px',
                'flex': 1
            }),
            
            html.Div([
                html.Span(id='connection-status', 
                         children="🔴 Nicht verbunden",
                         style={'fontSize': '12px', 'color': '#e74c3c'})
            ])
            
        ], style={
            'backgroundColor': self.brand_colors['light'],
            'padding': '10px 20px',
            'borderBottom': '1px solid #dee2e6',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'space-between'
        })
    
    def create_status_container(self) -> html.Div:
        """Erstelle Status-Container"""
        return html.Div([
            html.Div(id='status-container', children=[
                self.create_loading_status_card()
            ])
        ], style={'padding': '10px 20px'})
    
    def create_status_cards(self, status_data: Dict[str, Any]) -> html.Div:
        """
        Erstelle Status-Karten basierend auf API-Daten
        
        Args:
            status_data: System-Status von API
            
        Returns:
            html.Div: Status-Karten
        """
        try:
            cards = []
            
            # System-Status Karte
            system_status = status_data.get('status', 'unknown')
            system_color = self.brand_colors['success'] if system_status == 'healthy' else self.brand_colors['danger']
            
            cards.append(self.create_status_card(
                "System",
                system_status.title(),
                "fas fa-server",
                system_color
            ))
            
            # Datenbank-Status
            db_status = status_data.get('database_status', 'unknown')
            db_color = self.brand_colors['success'] if db_status == 'connected' else self.brand_colors['danger']
            
            cards.append(self.create_status_card(
                "Datenbank", 
                db_status.title(),
                "fas fa-database",
                db_color
            ))
            
            # Plugin-Status
            active_plugins = status_data.get('active_plugins', [])
            plugin_count = len(active_plugins)
            
            cards.append(self.create_status_card(
                "Plugins",
                f"{plugin_count} Aktiv",
                "fas fa-plug",
                self.brand_colors['info']
            ))
            
            # Performance-Metriken
            performance = status_data.get('performance_metrics', {})
            total_users = performance.get('total_users', 0)
            
            cards.append(self.create_status_card(
                "Benutzer",
                str(total_users),
                "fas fa-users",
                self.brand_colors['primary']
            ))
            
            return html.Div(cards, style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))',
                'gap': '15px',
                'marginBottom': '20px'
            })
            
        except Exception as e:
            return html.Div(f"Fehler beim Erstellen der Status-Karten: {str(e)}", 
                          style={'color': self.brand_colors['danger']})
    
    def create_status_card(self, title: str, value: str, icon: str, color: str) -> html.Div:
        """
        Erstelle einzelne Status-Karte
        
        Args:
            title: Titel der Karte
            value: Wert/Status
            icon: FontAwesome Icon-Klasse
            color: Farbe
            
        Returns:
            html.Div: Status-Karte
        """
        return html.Div([
            html.Div([
                html.I(className=icon, style={'fontSize': '24px', 'color': color}),
                html.Div([
                    html.H4(value, style={'margin': 0, 'color': color, 'fontSize': '18px'}),
                    html.P(title, style={'margin': 0, 'color': '#7f8c8d', 'fontSize': '12px'})
                ], style={'marginLeft': '15px'})
            ], style={
                'display': 'flex',
                'alignItems': 'center'
            })
        ], style={
            'backgroundColor': 'white',
            'padding': '15px',
            'borderRadius': '8px',
            'border': f'1px solid {color}',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        })
    
    def create_loading_status_card(self) -> html.Div:
        """Erstelle Loading-Status für initiale Anzeige"""
        return html.Div([
            html.Div([
                html.I(className="fas fa-spinner fa-spin", 
                      style={'fontSize': '20px', 'color': self.brand_colors['primary']}),
                html.P("System-Status wird geladen...", 
                      style={'margin': 0, 'marginLeft': '10px', 'color': '#7f8c8d'})
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={
            'backgroundColor': self.brand_colors['light'],
            'padding': '15px',
            'borderRadius': '8px',
            'border': f'1px solid {self.brand_colors["primary"]}'
        })
    
    def create_action_button(self, text: str, button_id: str, icon: str = "", 
                           color: str = "primary", size: str = "normal") -> html.Button:
        """
        Erstelle Action-Button
        
        Args:
            text: Button-Text
            button_id: Button-ID
            icon: FontAwesome Icon (optional)
            color: Button-Farbe
            size: Button-Größe (small, normal, large)
            
        Returns:
            html.Button: Action-Button
        """
        # Größen-Mapping
        size_styles = {
            'small': {'padding': '5px 10px', 'fontSize': '12px'},
            'normal': {'padding': '8px 16px', 'fontSize': '14px'},
            'large': {'padding': '12px 24px', 'fontSize': '16px'}
        }
        
        button_style = {
            'backgroundColor': self.brand_colors.get(color, self.brand_colors['primary']),
            'color': 'white',
            'border': 'none',
            'borderRadius': '4px',
            'cursor': 'pointer',
            'display': 'flex',
            'alignItems': 'center',
            'gap': '5px'
        }
        
        button_style.update(size_styles.get(size, size_styles['normal']))
        
        children = []
        if icon:
            children.append(html.I(className=icon))
        children.append(text)
        
        return html.Button(
            children,
            id=button_id,
            style=button_style
        )
    
    def create_data_table(self, data: List[Dict], columns: List[str], 
                         table_id: str = "data-table") -> html.Table:
        """
        Erstelle Daten-Tabelle
        
        Args:
            data: Tabellen-Daten
            columns: Spalten-Namen
            table_id: Tabellen-ID
            
        Returns:
            html.Table: Daten-Tabelle
        """
        if not data:
            return html.Div("Keine Daten verfügbar", style={'textAlign': 'center', 'color': '#7f8c8d'})
        
        # Header
        header = html.Thead([
            html.Tr([
                html.Th(col, style={
                    'backgroundColor': self.brand_colors['primary'],
                    'color': 'white',
                    'padding': '12px',
                    'textAlign': 'left'
                }) for col in columns
            ])
        ])
        
        # Rows
        rows = []
        for i, row in enumerate(data):
            cells = []
            for col in columns:
                value = row.get(col, "")
                cells.append(html.Td(str(value), style={
                    'padding': '8px 12px',
                    'borderBottom': '1px solid #dee2e6'
                }))
            
            rows.append(html.Tr(cells, style={
                'backgroundColor': '#f8f9fa' if i % 2 == 0 else 'white'
            }))
        
        tbody = html.Tbody(rows)
        
        return html.Table([header, tbody], 
                         id=table_id,
                         style={
                             'width': '100%',
                             'borderCollapse': 'collapse',
                             'backgroundColor': 'white',
                             'borderRadius': '8px',
                             'overflow': 'hidden',
                             'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                         })
    
    def create_footer(self) -> html.Div:
        """Erstelle Footer"""
        return html.Footer([
            html.Div([
                html.P([
                    "© 2024 DA-KI Portfolio Management | ",
                    html.A("GitHub", href="https://github.com/MarcoFPO/DA-KI", target="_blank"),
                    " | Version 2.0"
                ], style={'margin': 0, 'fontSize': '12px', 'color': '#7f8c8d'}),
                html.P(f"Letzte Aktualisierung: {datetime.now().strftime('%d.%m.%Y %H:%M')}", 
                      style={'margin': 0, 'fontSize': '10px', 'color': '#bdc3c7'})
            ], style={'textAlign': 'center'})
        ], style={
            'backgroundColor': self.brand_colors['dark'],
            'padding': '20px',
            'marginTop': '40px'
        })
    
    def create_modal(self, modal_id: str, title: str, content: html.Div, 
                    show_close: bool = True) -> html.Div:
        """
        Erstelle Modal-Dialog
        
        Args:
            modal_id: Modal-ID
            title: Modal-Titel
            content: Modal-Inhalt
            show_close: Zeige Schließen-Button
            
        Returns:
            html.Div: Modal-Dialog
        """
        return html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.H4(title, style={'margin': 0}),
                        html.Button("×", id=f"{modal_id}-close", 
                                  style={'border': 'none', 'background': 'none', 'fontSize': '24px'})
                        if show_close else None
                    ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}),
                    html.Hr(),
                    content
                ], style={
                    'backgroundColor': 'white',
                    'padding': '20px',
                    'borderRadius': '8px',
                    'maxWidth': '600px',
                    'width': '90%',
                    'maxHeight': '80vh',
                    'overflow': 'auto'
                })
            ], style={
                'position': 'fixed',
                'top': 0,
                'left': 0,
                'width': '100%',
                'height': '100%',
                'backgroundColor': 'rgba(0,0,0,0.5)',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'zIndex': 1000
            })
        ], id=modal_id, style={'display': 'none'})


# Export
__all__ = ['LayoutComponents']