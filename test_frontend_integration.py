#!/usr/bin/env python3
"""
Test-Script für Frontend-Integration
Testet die migrierte Dashboard-Architektur mit neuer Plugin-basierter API
"""

import sys
import os
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.frontend.dashboard_app import create_daki_dashboard_app
except ImportError as e:
    print(f"Import-Fehler: {e}")
    print("Stelle sicher, dass alle Abhängigkeiten installiert sind:")
    print("pip install dash plotly requests")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_frontend_integration():
    """Test Frontend-Integration"""
    print("🧪 Teste DA-KI Frontend-Integration...")
    print("=" * 50)
    
    try:
        # 1. Dashboard-App erstellen
        print("1️⃣ Erstelle Dashboard-App...")
        dashboard_app = create_daki_dashboard_app(api_base_url="http://localhost:8000")
        print("✅ Dashboard-App erfolgreich erstellt")
        
        # 2. Module testen
        print("2️⃣ Teste Module-Initialisierung...")
        
        # Orchestrator testen
        orchestrator_status = dashboard_app.orchestrator.get_orchestrator_status()
        print(f"✅ Orchestrator Status: {orchestrator_status['orchestrator_version']}")
        
        # Module-Status prüfen
        for module_name, status in orchestrator_status['modules'].items():
            print(f"   📦 {module_name}: {status['status']}")
        
        # 3. API-Verbindung testen (Mock)
        print("3️⃣ Teste API-Verbindung...")
        test_response = dashboard_app.make_api_call("/health/liveness")
        if "error" in test_response:
            print(f"⚠️  API nicht verfügbar: {test_response['error']}")
            print("   💡 Starte das Backend mit: python src/main_improved.py")
        else:
            print("✅ API-Verbindung erfolgreich")
        
        # 4. Layout-Komponenten testen
        print("4️⃣ Teste Layout-Komponenten...")
        layout_components = dashboard_app.layout_components
        
        # Test-Header erstellen
        header = layout_components.create_main_header()
        print("✅ Header-Komponente erstellt")
        
        # Test-Status-Karte erstellen
        status_card = layout_components.create_status_card("Test", "OK", "fas fa-check", "#27ae60")
        print("✅ Status-Karte erstellt")
        
        # 5. Module-Content testen
        print("5️⃣ Teste Module-Content...")
        
        # KI-Wachstumsprognose
        ki_content = dashboard_app.ki_wachstumsprognose.create_content()
        print("✅ KI-Wachstumsprognose Content erstellt")
        
        # Live-Monitoring
        monitoring_content = dashboard_app.live_monitoring.create_content()
        print("✅ Live-Monitoring Content erstellt")
        
        # 6. Dashboard-Layout testen
        print("6️⃣ Teste Dashboard-Layout...")
        app_layout = dashboard_app.app.layout
        print("✅ Dashboard-Layout erfolgreich erstellt")
        
        print("\n" + "=" * 50)
        print("🎉 Frontend-Integration-Test ERFOLGREICH!")
        print("\n📊 Bereit zum Starten:")
        print("   1. Backend starten: python src/main_improved.py")
        print("   2. Frontend starten: python test_frontend_integration.py --run")
        print("   3. Browser öffnen: http://10.1.1.110:8054")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Frontend-Integration-Test FEHLGESCHLAGEN!")
        print(f"Fehler: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def run_dashboard():
    """Starte Dashboard-Server"""
    print("🚀 Starte DA-KI Dashboard v2.0...")
    
    try:
        dashboard_app = create_daki_dashboard_app(api_base_url="http://localhost:8000")
        dashboard_app.run_server(debug=True, host='0.0.0.0', port=8054)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard gestoppt")
    except Exception as e:
        print(f"\n❌ Fehler beim Starten des Dashboards: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--run":
        run_dashboard()
    else:
        success = test_frontend_integration()
        sys.exit(0 if success else 1)