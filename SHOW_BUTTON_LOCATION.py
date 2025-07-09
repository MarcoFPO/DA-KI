#!/usr/bin/env python3
"""
Zeigt genau wo der Button und Progress-Bar im korrigierten Dashboard zu finden sind
"""
import requests
import re

def show_button_location():
    """Zeigt die genaue Position des Buttons auf der Seite"""
    
    print("🔍 Suche Button und Progress-Bar auf http://10.1.1.110:8054...")
    
    try:
        response = requests.get("http://10.1.1.110:8054/", timeout=10)
        html_content = response.text
        
        print(f"📊 HTML-Länge: {len(html_content)} Zeichen")
        print(f"📊 HTTP Status: {response.status_code}")
        
        # Suche nach spezifischen Elementen
        elements_to_find = [
            "refresh-growth-btn",
            "progress-container-real", 
            "progress-bar-real",
            "Prognose neu berechnen",
            "KORRIGIERT",
            "🔄 Prognose neu berechnen"
        ]
        
        print("\n🎯 Suche nach korrigierten Elementen:")
        for element in elements_to_find:
            if element in html_content:
                print(f"✅ GEFUNDEN: '{element}'")
                # Zeige Kontext
                start = max(0, html_content.find(element) - 100)
                end = min(len(html_content), html_content.find(element) + 200)
                context = html_content[start:end]
                print(f"   Kontext: ...{context}...")
                print()
            else:
                print(f"❌ NICHT GEFUNDEN: '{element}'")
        
        # Prüfe Titel
        title_match = re.search(r'<title>(.*?)</title>', html_content)
        if title_match:
            print(f"\n📄 Seiten-Titel: {title_match.group(1)}")
        
        # Zeige ersten Teil der Seite
        print("\n📖 Erste 500 Zeichen der Seite:")
        print("=" * 60)
        print(html_content[:500])
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

if __name__ == "__main__":
    show_button_location()