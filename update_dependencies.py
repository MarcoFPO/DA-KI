#!/usr/bin/env python3
"""
Aktualisiert alle Abhängigkeiten auf kompatible Versionen
"""

import subprocess
import sys
import os

def run_command(cmd, description=""):
    """Führe Kommando aus mit Error-Handling"""
    print(f"🔧 {description}")
    print(f"   Kommando: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"✅ Erfolgreich")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()[:200]}")
        else:
            print(f"❌ Fehler (Code {result.returncode})")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()[:200]}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout nach 5 Minuten")
        return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def update_system():
    """Aktualisiere System-Komponenten"""
    print("🚀 Starte System-Update...")
    
    # 1. System-Pakete aktualisieren
    if run_command("sudo apt update", "System-Paketliste aktualisieren"):
        run_command("sudo apt upgrade -y python3 python3-pip", "Python3 System-Pakete aktualisieren")
    
    # 2. NumPy/Pandas auf kompatible Versionen downgraden
    print("\n📦 Repariere NumPy/Pandas Kompatibilität...")
    
    # Mit --break-system-packages da es extern verwaltet ist
    commands = [
        "python3 -m pip install 'numpy>=1.24.0,<2.0.0' --upgrade --break-system-packages --force-reinstall",
        "python3 -m pip install 'pandas>=2.1.4,<2.3.0' --upgrade --break-system-packages --force-reinstall", 
        "python3 -m pip install 'dash>=2.18.1' --upgrade --break-system-packages",
        "python3 -m pip install 'plotly>=5.24.1' --upgrade --break-system-packages",
        "python3 -m pip install 'fastapi>=0.115.0' --upgrade --break-system-packages",
        "python3 -m pip install 'uvicorn[standard]>=0.34.0' --upgrade --break-system-packages"
    ]
    
    for cmd in commands:
        run_command(cmd, f"Installiere Paket: {cmd.split()[4]}")
    
    # 3. Versions-Check
    print("\n📊 Versions-Check nach Update:")
    check_commands = [
        "python3 -c \"import numpy; print(f'NumPy: {numpy.__version__}')\"",
        "python3 -c \"import pandas; print(f'Pandas: {pandas.__version__}')\"", 
        "python3 -c \"import dash; print(f'Dash: {dash.__version__}')\"",
        "python3 -c \"import plotly; print(f'Plotly: {plotly.__version__}')\"",
        "python3 -c \"import fastapi; print(f'FastAPI: {fastapi.__version__}')\"",
        "python3 -c \"import uvicorn; print(f'Uvicorn: {uvicorn.__version__}')\""
    ]
    
    for cmd in check_commands:
        run_command(cmd, "Versions-Check")
    
    print("\n🎯 Update abgeschlossen!")
    print("⚠️  Starten Sie das Dashboard neu, um die Änderungen zu übernehmen.")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("⚠️  Dieses Script benötigt Root-Rechte für System-Updates")
        print("   Führen Sie aus: sudo python3 update_dependencies.py")
        sys.exit(1)
    
    update_system()