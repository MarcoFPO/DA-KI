#!/usr/bin/env python3
"""
Test-Script zur Überprüfung der Action-Button Integration
"""

# Import aller Module
from ki_wachstumsprognose_module import create_wachstumsprognose_instance
from live_monitoring_module import create_live_monitoring_instance
from frontend_tabelle_module import (
    create_frontend_tabelle_instance,
    create_action_button_integration
)

def test_action_button_integration():
    """Teste Action-Button Integration"""
    print("🔍 Testing Action-Button Integration...")
    
    # Module erstellen
    wachstumsprognose = create_wachstumsprognose_instance()
    live_monitoring = create_live_monitoring_instance()
    frontend_tabelle = create_frontend_tabelle_instance()
    
    # Test 1: Action Integration erstellen
    print("\n📋 Test 1: Action Button Integration erstellen")
    action_integration = create_action_button_integration(live_monitoring)
    print(f"✅ Action Integration erstellt: {type(action_integration)}")
    
    # Test 2: Interface setzen
    print("\n📋 Test 2: Interface an Tabelle setzen")
    frontend_tabelle.set_action_button_interface(action_integration)
    print(f"✅ Interface gesetzt: {frontend_tabelle.action_button_interface is not None}")
    
    # Test 3: Aktien-Daten laden
    print("\n📋 Test 3: Aktien-Daten laden")
    aktien_daten = wachstumsprognose.get_aktien_daten()
    print(f"✅ Aktien geladen: {len(aktien_daten)} Aktien")
    
    if aktien_daten:
        erste_aktie = aktien_daten[0]
        print(f"   Erste Aktie: {erste_aktie.get('symbol')} - {erste_aktie.get('name', 'N/A')}")
    
    # Test 4: Action-Button erstellen
    print("\n📋 Test 4: Action-Button für erste Aktie erstellen")
    if aktien_daten:
        action_cell = action_integration.create_action_column_button(aktien_daten[0], 0)
        print(f"✅ Action-Button erstellt: {type(action_cell)}")
        try:
            button = action_cell.children
            print(f"   Button-Inhalte: {button}")
        except:
            print(f"   Button-Inhalte: Nicht verfügbar")
    
    # Test 5: Tabelle mit Actions erstellen
    print("\n📋 Test 5: Tabelle mit Action-Buttons erstellen")
    tabelle_mit_actions = frontend_tabelle.create_wachstumsprognose_tabelle_mit_actions(aktien_daten[:3])  # Nur erste 3 für Test
    print(f"✅ Tabelle erstellt: {type(tabelle_mit_actions)}")
    
    # Test 6: Tabellen-Header prüfen
    print("\n📋 Test 6: Header-Spalten prüfen")
    if hasattr(tabelle_mit_actions, 'children') and len(tabelle_mit_actions.children) > 0:
        thead = tabelle_mit_actions.children[0]  # thead
        if hasattr(thead, 'children') and len(thead.children) > 0:
            header_row = thead.children[0]  # tr
            if hasattr(header_row, 'children'):
                spalten_anzahl = len(header_row.children)
                print(f"✅ Header-Spalten: {spalten_anzahl}")
                
                # Letzte Spalte sollte "🎯 Aktion" sein
                if spalten_anzahl > 0:
                    letzte_spalte = header_row.children[-1]
                    if hasattr(letzte_spalte, 'children'):
                        spalten_text = letzte_spalte.children
                        print(f"   Letzte Spalte: {spalten_text}")
    
    # Test 7: Datenzeilen prüfen
    print("\n📋 Test 7: Datenzeilen mit Action-Buttons prüfen")
    if hasattr(tabelle_mit_actions, 'children') and len(tabelle_mit_actions.children) > 1:
        tbody = tabelle_mit_actions.children[1]  # tbody
        if hasattr(tbody, 'children') and len(tbody.children) > 0:
            erste_zeile = tbody.children[0]  # tr
            if hasattr(erste_zeile, 'children'):
                zellen_anzahl = len(erste_zeile.children)
                print(f"✅ Zellen in erster Datenzeile: {zellen_anzahl}")
                
                # Letzte Zelle sollte Action-Button enthalten
                if zellen_anzahl > 0:
                    letzte_zelle = erste_zeile.children[-1]
                    if hasattr(letzte_zelle, 'children') and len(letzte_zelle.children) > 0:
                        button = letzte_zelle.children[0]
                        if hasattr(button, 'children'):
                            button_text = button.children
                            print(f"   Action-Button Text: {button_text}")
                            print(f"   Button ID: {getattr(button, 'id', 'N/A')}")
                        else:
                            print(f"   ❌ Kein Button-Text gefunden")
                    else:
                        print(f"   ❌ Keine Button-Inhalte in letzter Zelle")
                else:
                    print(f"   ❌ Keine Zellen in Datenzeile")
    
    print("\n🎯 Test abgeschlossen!")
    return True

if __name__ == '__main__':
    test_action_button_integration()