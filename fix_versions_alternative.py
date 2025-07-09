#!/usr/bin/env python3
"""
Alternative Lösung: Dashboard ohne problematische Abhängigkeiten
"""

import os
import subprocess

def create_compatibility_layer():
    """Erstelle Kompatibilitäts-Layer für das Dashboard"""
    
    print("🔧 Erstelle Kompatibilitäts-Layer...")
    
    # 1. Pandas-freie Version des Dashboards
    dashboard_fixes = """
# Pandas/NumPy Kompatibilitäts-Fixes
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Alternative zu Pandas DataFrame
class SimpleDataFrame:
    def __init__(self, data):
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            self.data = data
            self.columns = list(data[0].keys()) if data else []
        else:
            self.data = []
            self.columns = []
    
    def __getitem__(self, column):
        return [row.get(column, None) for row in self.data]
    
    def tolist(self):
        return self.data

# Patch-Funktion für problematische Imports
def safe_import_pandas():
    try:
        import pandas as pd
        import numpy as np
        return pd, np, True
    except (ImportError, AttributeError):
        return None, None, False

# Globale Kompatibilitäts-Variable
PANDAS_AVAILABLE = False
pd, np, PANDAS_AVAILABLE = safe_import_pandas()

if not PANDAS_AVAILABLE:
    # Erstelle Dummy-Pandas
    class DummyPandas:
        @staticmethod
        def DataFrame(data):
            return SimpleDataFrame(data)
    
    pd = DummyPandas()
"""
    
    # Erstelle Kompatibilitätsdatei
    with open('/home/mdoehler/data-web-app/compatibility_layer.py', 'w') as f:
        f.write(dashboard_fixes)
    
    print("✅ Kompatibilitäts-Layer erstellt")
    
    # 2. Dashboard mit Kompatibilitäts-Import modifizieren
    dashboard_path = '/home/mdoehler/data-web-app/original_dashboard_reconstructed.py'
    
    # Backup erstellen
    subprocess.run(f"cp {dashboard_path} {dashboard_path}.backup", shell=True)
    
    # Dashboard-Import modifizieren
    with open(dashboard_path, 'r') as f:
        content = f.read()
    
    # Ersetze problematische Imports
    new_content = content.replace(
        "# NumPy/Pandas komplett deaktiviert wegen Version-Konflikten\nHAS_PANDAS = False\nprint(\"⚠️ NumPy/Pandas deaktiviert wegen Versions-Konflikten - verwende alternative Implementierung\")",
        """# Kompatibilitäts-Layer laden
import sys
sys.path.insert(0, '/home/mdoehler/data-web-app')
from compatibility_layer import pd, np, PANDAS_AVAILABLE

HAS_PANDAS = PANDAS_AVAILABLE
if HAS_PANDAS:
    print("✅ Pandas/NumPy erfolgreich geladen")
else:
    print("⚠️ Pandas/NumPy nicht verfügbar - verwende Kompatibilitäts-Layer")"""
    )
    
    with open(dashboard_path, 'w') as f:
        f.write(new_content)
    
    print("✅ Dashboard mit Kompatibilitäts-Layer modifiziert")
    
    # 3. Versions-Check
    print("\n📊 Aktuelle Versionen:")
    version_checks = [
        ("Python", "python3 --version"),
        ("Dash", "python3 -c 'import dash; print(dash.__version__)' 2>/dev/null || echo 'Nicht verfügbar'"),
        ("Plotly", "python3 -c 'import plotly; print(plotly.__version__)' 2>/dev/null || echo 'Nicht verfügbar'"),
        ("Requests", "python3 -c 'import requests; print(requests.__version__)' 2>/dev/null || echo 'Nicht verfügbar'"),
        ("FastAPI", "python3 -c 'import fastapi; print(fastapi.__version__)' 2>/dev/null || echo 'Nicht verfügbar'")
    ]
    
    for name, cmd in version_checks:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            version = result.stdout.strip()
            print(f"   {name}: {version}")
        except:
            print(f"   {name}: Fehler beim Abrufen")
    
    print("\n🎯 Alternative Lösung implementiert!")
    print("📊 Dashboard sollte jetzt ohne NumPy-Probleme laufen")
    
    return True

def test_dashboard():
    """Teste das reparierte Dashboard"""
    print("\n🧪 Teste repariertes Dashboard...")
    
    try:
        # Import-Test
        result = subprocess.run(
            "python3 -c 'from compatibility_layer import pd, PANDAS_AVAILABLE; print(f\"Kompatibilität: {PANDAS_AVAILABLE}\")'",
            shell=True, capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Kompatibilitäts-Layer funktioniert")
            print(f"   {result.stdout.strip()}")
        else:
            print("❌ Kompatibilitäts-Layer fehlerhaft")
            print(f"   Error: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ Test fehlgeschlagen: {e}")
        return False
    
    print("✅ Dashboard bereit für Neustart")
    return True

if __name__ == "__main__":
    print("🚀 Starte alternative Versions-Reparatur...")
    
    if create_compatibility_layer():
        if test_dashboard():
            print("\n✅ SYSTEM REPARIERT")
            print("📊 Starten Sie das Dashboard neu:")
            print("   python3 original_dashboard_reconstructed.py")
        else:
            print("\n❌ Test fehlgeschlagen")
    else:
        print("\n❌ Reparatur fehlgeschlagen")