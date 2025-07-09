#!/usr/bin/env python3
"""
Korrekter Dashboard-Start
"""

import sys
import os
sys.path.insert(0, '/home/mdoehler/data-web-app/frontend')

from dashboard_orchestrator import create_dashboard_orchestrator

if __name__ == '__main__':
    print("🔧 Starte KORREKTES modulares DA-KI Dashboard...")
    print("⚠️  Verwende dashboard_orchestrator.py mit allen Updates!")
    
    orchestrator = create_dashboard_orchestrator("🚀 DA-KI Dashboard (KORREKT)")
    
    # Verifikation
    layout_str = str(orchestrator.app.layout)
    if 'refresh-btn' in layout_str:
        print("✅ Korrekte Button-ID: refresh-btn")
    if 'progress-container' in layout_str:
        print("✅ Fortschrittsbalken vorhanden")
    
    print("📊 URL: http://10.1.1.110:8054")
    print("🎯 Dashboard mit funktionierendem 'Prognose neu berechnen' Button!")
    
    orchestrator.run_server(debug=False, host='0.0.0.0', port=8054)