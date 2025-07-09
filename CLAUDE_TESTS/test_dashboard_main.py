#!/usr/bin/env python3
"""
Test-Script für modularen Dashboard
"""

import sys
import os
sys.path.append('/home/mdoehler/data-web-app/frontend')

from dashboard_orchestrator import create_dashboard_orchestrator

if __name__ == '__main__':
    print("🔧 Starte Test für modularen DA-KI Dashboard...")
    orchestrator = create_dashboard_orchestrator()
    orchestrator.run_server(debug=False, host='0.0.0.0', port=8054)