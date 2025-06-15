#!/usr/bin/env python3
"""
DA-KI Dashboard Vollständig Modular - Orchestrator-basierte Architektur
Alle Teilprojekte als vollständig isolierte Module mit definierten Schnittstellen
"""

from dashboard_orchestrator import create_dashboard_orchestrator

if __name__ == '__main__':
    # Vollständig modulares Dashboard erstellen
    orchestrator = create_dashboard_orchestrator("🚀 DA-KI Dashboard")
    
    # Server starten (NUR IP 10.1.1.110 und Port 8054)
    orchestrator.run_server(debug=False, host='0.0.0.0', port=8054)