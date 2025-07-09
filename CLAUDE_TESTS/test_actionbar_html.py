#!/usr/bin/env python3
"""
Test für Action-Bar HTML-Struktur
"""

import sys
sys.path.append('/home/mdoehler/data-web-app/frontend')

from frontend_layout_module import create_frontend_layout_instance

def test_action_bar_html():
    print("🔧 Teste Action-Bar HTML-Struktur...")
    
    # Erstelle Layout-Instanz
    layout = create_frontend_layout_instance()
    
    # Erstelle Action-Bar
    action_bar = layout.create_action_bar()
    
    print(f"✅ Action-Bar erstellt: {type(action_bar)}")
    print(f"📋 Action-Bar Struktur:")
    
    # Untersuche Struktur
    def print_element_structure(element, indent=0):
        prefix = "  " * indent
        print(f"{prefix}- {type(element).__name__}")
        
        if hasattr(element, 'id') and element.id:
            print(f"{prefix}  ID: {element.id}")
        
        if hasattr(element, 'children') and element.children:
            if isinstance(element.children, list):
                for child in element.children:
                    print_element_structure(child, indent + 1)
            else:
                print_element_structure(element.children, indent + 1)
    
    print_element_structure(action_bar)
    
    # Teste spezifische IDs
    layout_str = str(action_bar)
    required_ids = ['refresh-btn', 'progress-container', 'progress-bar', 'progress-text']
    
    print(f"\n🔍 ID-Überprüfung:")
    for required_id in required_ids:
        if required_id in layout_str:
            print(f"✅ {required_id} gefunden")
        else:
            print(f"❌ {required_id} FEHLT")
    
    print(f"\n📄 HTML-String (erste 500 Zeichen):")
    print(layout_str[:500])

if __name__ == '__main__':
    test_action_bar_html()