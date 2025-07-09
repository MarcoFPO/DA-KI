#!/usr/bin/env python3
"""
Debug Test für Callback-Registrierung
"""

import sys
sys.path.append('/home/mdoehler/data-web-app/frontend')

from dashboard_orchestrator import create_dashboard_orchestrator

def test_callback_registration():
    print("🔧 Teste Callback-Registrierung...")
    
    # Erstelle Orchestrator
    orchestrator = create_dashboard_orchestrator()
    
    # Prüfe registrierte Callbacks
    callbacks = orchestrator.frontend_callbacks.get_registered_callbacks()
    print(f"✅ Registrierte Callbacks: {callbacks}")
    
    # Prüfe App-Layout
    layout = orchestrator.app.layout
    print(f"✅ Layout erstellt: {type(layout)}")
    
    # Prüfe ob refresh-btn im Layout ist
    import json
    layout_str = str(layout)
    if 'refresh-btn' in layout_str:
        print("✅ refresh-btn gefunden im Layout")
    else:
        print("❌ refresh-btn NICHT im Layout gefunden")
    
    # Prüfe Progress-Elemente
    progress_elements = ['progress-container', 'progress-bar', 'progress-text']
    for element in progress_elements:
        if element in layout_str:
            print(f"✅ {element} gefunden im Layout")
        else:
            print(f"❌ {element} NICHT im Layout gefunden")

if __name__ == '__main__':
    test_callback_registration()