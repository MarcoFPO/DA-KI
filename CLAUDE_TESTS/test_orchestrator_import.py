#!/usr/bin/env python3
"""
Test für Orchestrator-Import
"""

import sys
sys.path.append('/home/mdoehler/data-web-app/frontend')

print("🔧 Teste Orchestrator-Import...")

from dashboard_orchestrator import create_dashboard_orchestrator

orchestrator = create_dashboard_orchestrator()
print(f"✅ Orchestrator erstellt: {type(orchestrator)}")

# Prüfe App-Layout
layout = orchestrator.app.layout
layout_str = str(layout)

# Suche nach Button-IDs
if 'refresh-btn' in layout_str:
    print("✅ KORREKT: refresh-btn gefunden (mein Code)")
elif 'refresh-growth-btn' in layout_str:
    print("❌ FALSCH: refresh-growth-btn gefunden (altes Dashboard)")
else:
    print("❓ UNBEKANNT: Keine Button-ID gefunden")

# Suche nach Progress-Elementen
progress_elements = ['progress-container', 'progress-bar', 'progress-text']
found_count = 0
for element in progress_elements:
    if element in layout_str:
        found_count += 1
        print(f"✅ {element} gefunden")
    else:
        print(f"❌ {element} FEHLT")

print(f"\n📊 Progress-Elemente gefunden: {found_count}/3")

# Titel prüfen
if 'DA-KI Dashboard' in layout_str:
    print("✅ Korrekter Titel gefunden")
else:
    print("❌ Falscher Titel")

print(f"\n📄 Layout-String (erste 200 Zeichen):")
print(layout_str[:200])