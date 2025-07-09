# CLAUDE TEST UMGEBUNG - ISOLIERT

⚠️ **WARNUNG: ALLE DATEIEN IN DIESEM ORDNER SIND NUR FÜR CLAUDE-TESTS**

## Zweck
Dieser Ordner enthält ausschließlich Test-Code von Claude, um die Testumgebung von der Production-Umgebung zu isolieren.

## Inhalt
- `test_*.py` - Test-Scripts von Claude
- `debug_*.py` - Debug-Scripts von Claude  
- `simple_*.py` - Einfache Test-Implementierungen von Claude
- Alle anderen experimentellen Scripts von Claude

## WICHTIG
- ⛔ **NIEMALS** Code aus diesem Ordner in Production verwenden
- ⛔ **NIEMALS** diese Tests als funktionsfähig ansehen
- ✅ Nur zur Diagnose und Debugging verwenden
- ✅ Alle Scripts haben "CLAUDE_TEST" Marker im Code

## Production Dashboard
Das echte Dashboard liegt in:
- `/home/mdoehler/data-web-app/frontend/dashboard_orchestrator.py`
- Oder andere Production-Files im Hauptverzeichnis

Erstellt von: Claude AI (Assistent)
Datum: $(date)