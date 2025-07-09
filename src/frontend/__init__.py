"""
DA-KI Frontend Package
Migrierte Frontend-Architektur für neue Plugin-basierte API
"""

from .dashboard_app import DAKIDashboardApp, create_daki_dashboard_app
from .orchestrator import DashboardOrchestrator

__version__ = "2.0.0"
__all__ = [
    'DAKIDashboardApp',
    'create_daki_dashboard_app', 
    'DashboardOrchestrator'
]