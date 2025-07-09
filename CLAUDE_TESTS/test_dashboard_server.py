#!/usr/bin/env python3
"""
DA-KI Test & Monitoring Dashboard Server
Port 8055 - Comprehensive Service Testing & Health Monitoring
"""

from flask import Flask, render_template_string, jsonify, request
import requests
import json
import time
from datetime import datetime
import subprocess
import socket

app = Flask(__name__)

# Target server configuration
TARGET_SERVER = "10.1.1.110"
SERVICES = {
    "api_backend": {"port": 8003, "name": "API Backend", "health_endpoint": "/"},
    "frontend_dashboard": {"port": 8054, "name": "Frontend Dashboard", "health_endpoint": "/"},
    "test_dashboard": {"port": 8055, "name": "Test Dashboard", "health_endpoint": "/health"}
}

def test_service_connectivity(host, port):
    """Test TCP connectivity to a service"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def test_api_endpoint(url, timeout=5):
    """Test API endpoint and return response details"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            "status": "success",
            "status_code": response.status_code,
            "response_time_ms": response_time,
            "content_type": response.headers.get('content-type', 'unknown'),
            "content_length": len(response.content),
            "data": response.json() if 'application/json' in response.headers.get('content-type', '') else None
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "response_time_ms": None
        }

def run_comprehensive_tests():
    """Run comprehensive test suite"""
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "target_server": TARGET_SERVER,
        "network_tests": {},
        "service_tests": {},
        "api_tests": {},
        "integration_tests": {}
    }
    
    # Network connectivity tests
    for service_id, config in SERVICES.items():
        port = config["port"]
        is_reachable = test_service_connectivity(TARGET_SERVER, port)
        test_results["network_tests"][service_id] = {
            "name": config["name"],
            "port": port,
            "reachable": is_reachable,
            "url": f"http://{TARGET_SERVER}:{port}"
        }
    
    # Service health tests
    for service_id, config in SERVICES.items():
        if test_results["network_tests"][service_id]["reachable"]:
            url = f"http://{TARGET_SERVER}:{config['port']}{config['health_endpoint']}"
            health_result = test_api_endpoint(url)
            test_results["service_tests"][service_id] = health_result
        else:
            test_results["service_tests"][service_id] = {"status": "unreachable"}
    
    # Specific API endpoint tests
    api_endpoints = [
        {"name": "API Health", "url": f"http://{TARGET_SERVER}:8003/"},
        {"name": "Progress API", "url": f"http://{TARGET_SERVER}:8003/api/calculation/progress"},
        {"name": "Growth Prediction", "url": f"http://{TARGET_SERVER}:8003/api/wachstumsprognose/top10"},
        {"name": "Frontend Dashboard", "url": f"http://{TARGET_SERVER}:8054/"},
    ]
    
    for endpoint in api_endpoints:
        test_results["api_tests"][endpoint["name"]] = test_api_endpoint(endpoint["url"])
    
    # Integration tests
    try:
        # Test if frontend can reach API
        api_health = test_results["api_tests"].get("API Health", {})
        frontend_health = test_results["api_tests"].get("Frontend Dashboard", {})
        
        integration_status = "success" if (
            api_health.get("status") == "success" and 
            frontend_health.get("status") == "success"
        ) else "failed"
        
        test_results["integration_tests"]["frontend_api_connectivity"] = {
            "status": integration_status,
            "description": "Frontend can reach API Backend"
        }
    except Exception as e:
        test_results["integration_tests"]["error"] = str(e)
    
    return test_results

@app.route('/')
def dashboard():
    """Main test dashboard"""
    html_template = '''
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DA-KI Test & Monitoring Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { text-align: center; color: #2c3e50; margin-bottom: 30px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .status-success { color: #27ae60; font-weight: bold; }
        .status-error { color: #e74c3c; font-weight: bold; }
        .status-warning { color: #f39c12; font-weight: bold; }
        .btn { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #2980b9; }
        .log { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; font-family: monospace; height: 300px; overflow-y: scroll; }
        .service-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
        .service-card { padding: 15px; border-radius: 5px; text-align: center; }
        .service-online { background: #d5f4e6; border: 2px solid #27ae60; }
        .service-offline { background: #fadbd8; border: 2px solid #e74c3c; }
        .metric { display: flex; justify-content: space-between; margin: 10px 0; }
        .timestamp { color: #7f8c8d; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 DA-KI Test & Monitoring Dashboard</h1>
            <p>Port 8055 - Target Server: {{ target_server }}</p>
            <p class="timestamp">Last Update: <span id="last-update">{{ timestamp }}</span></p>
        </div>

        <div style="text-align: center; margin-bottom: 20px;">
            <button class="btn" onclick="runTests()">🔄 Tests ausführen</button>
            <button class="btn" onclick="toggleAutoRefresh()">⏰ Auto-Refresh</button>
            <button class="btn" onclick="exportResults()">📄 Ergebnisse exportieren</button>
        </div>

        <div class="grid">
            <!-- Service Status Overview -->
            <div class="card">
                <h3>📊 Service Status Overview</h3>
                <div class="service-grid">
                    <div class="service-card service-offline" id="api-status">
                        <h4>API Backend</h4>
                        <p>Port 8003</p>
                        <p id="api-status-text">❌ Offline</p>
                    </div>
                    <div class="service-card service-offline" id="frontend-status">
                        <h4>Frontend</h4>
                        <p>Port 8054</p>
                        <p id="frontend-status-text">❌ Offline</p>
                    </div>
                    <div class="service-card service-online" id="test-status">
                        <h4>Test Dashboard</h4>
                        <p>Port 8055</p>
                        <p id="test-status-text">✅ Online</p>
                    </div>
                </div>
            </div>

            <!-- Network Tests -->
            <div class="card">
                <h3>🌐 Network Connectivity</h3>
                <div id="network-results">
                    <p>Klicken Sie auf "Tests ausführen" um zu starten...</p>
                </div>
            </div>

            <!-- API Tests -->
            <div class="card">
                <h3>🔌 API Endpoint Tests</h3>
                <div id="api-results">
                    <p>Klicken Sie auf "Tests ausführen" um zu starten...</p>
                </div>
            </div>

            <!-- Performance Metrics -->
            <div class="card">
                <h3>⚡ Performance Metrics</h3>
                <div id="performance-metrics">
                    <div class="metric">
                        <span>API Response Time:</span>
                        <span id="api-response-time">-</span>
                    </div>
                    <div class="metric">
                        <span>Frontend Load Time:</span>
                        <span id="frontend-load-time">-</span>
                    </div>
                    <div class="metric">
                        <span>Integration Status:</span>
                        <span id="integration-status">-</span>
                    </div>
                </div>
            </div>

            <!-- Test Log -->
            <div class="card">
                <h3>📝 Test Log</h3>
                <div class="log" id="test-log">
                    DA-KI Test Dashboard gestartet...\\n
                    Bereit für Tests auf {{ target_server }}\\n
                    ====================================\\n
                </div>
            </div>

            <!-- Quick Links -->
            <div class="card">
                <h3>🔗 Quick Links</h3>
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <a href="http://{{ target_server }}:8003" target="_blank" class="btn">🚀 API Backend</a>
                    <a href="http://{{ target_server }}:8054" target="_blank" class="btn">📊 Frontend Dashboard</a>
                    <a href="http://{{ target_server }}:8055/test-results" target="_blank" class="btn">📋 Test Results JSON</a>
                    <a href="http://{{ target_server }}:8055/health" target="_blank" class="btn">💓 Health Check</a>
                </div>
            </div>
        </div>
    </div>

    <script>
        let autoRefresh = false;
        let refreshInterval;

        function addToLog(message) {
            const log = document.getElementById('test-log');
            const timestamp = new Date().toLocaleTimeString();
            log.innerHTML += `[${timestamp}] ${message}\\n`;
            log.scrollTop = log.scrollHeight;
        }

        async function runTests() {
            addToLog("🔄 Starte Test-Suite...");
            
            try {
                const response = await fetch('/api/run-tests');
                const results = await response.json();
                
                updateDashboard(results);
                addToLog("✅ Test-Suite abgeschlossen");
                
                document.getElementById('last-update').textContent = new Date().toLocaleString();
            } catch (error) {
                addToLog(`❌ Test-Fehler: ${error.message}`);
            }
        }

        function updateDashboard(results) {
            // Update service status
            updateServiceStatus('api', results.service_tests.api_backend);
            updateServiceStatus('frontend', results.service_tests.frontend_dashboard);
            
            // Update network results
            const networkHtml = Object.entries(results.network_tests).map(([service, test]) => 
                `<div class="metric">
                    <span>${test.name} (${test.port}):</span>
                    <span class="${test.reachable ? 'status-success' : 'status-error'}">
                        ${test.reachable ? '✅ Erreichbar' : '❌ Nicht erreichbar'}
                    </span>
                </div>`
            ).join('');
            document.getElementById('network-results').innerHTML = networkHtml;
            
            // Update API results
            const apiHtml = Object.entries(results.api_tests).map(([name, test]) =>
                `<div class="metric">
                    <span>${name}:</span>
                    <span class="${test.status === 'success' ? 'status-success' : 'status-error'}">
                        ${test.status === 'success' ? '✅ OK' : '❌ Fehler'} 
                        ${test.response_time_ms ? `(${test.response_time_ms}ms)` : ''}
                    </span>
                </div>`
            ).join('');
            document.getElementById('api-results').innerHTML = apiHtml;
            
            // Update performance metrics
            const apiTest = results.api_tests['API Health'];
            if (apiTest && apiTest.response_time_ms) {
                document.getElementById('api-response-time').textContent = `${apiTest.response_time_ms}ms`;
            }
            
            const frontendTest = results.api_tests['Frontend Dashboard'];
            if (frontendTest && frontendTest.response_time_ms) {
                document.getElementById('frontend-load-time').textContent = `${frontendTest.response_time_ms}ms`;
            }
            
            const integrationStatus = results.integration_tests.frontend_api_connectivity;
            if (integrationStatus) {
                document.getElementById('integration-status').textContent = 
                    integrationStatus.status === 'success' ? '✅ OK' : '❌ Fehler';
            }
        }

        function updateServiceStatus(service, testResult) {
            const statusElement = document.getElementById(`${service}-status`);
            const textElement = document.getElementById(`${service}-status-text`);
            
            if (testResult && testResult.status === 'success') {
                statusElement.className = 'service-card service-online';
                textElement.textContent = '✅ Online';
            } else {
                statusElement.className = 'service-card service-offline';
                textElement.textContent = '❌ Offline';
            }
        }

        function toggleAutoRefresh() {
            autoRefresh = !autoRefresh;
            if (autoRefresh) {
                refreshInterval = setInterval(runTests, 30000); // 30 seconds
                addToLog("⏰ Auto-Refresh aktiviert (30s)");
            } else {
                clearInterval(refreshInterval);
                addToLog("⏰ Auto-Refresh deaktiviert");
            }
        }

        function exportResults() {
            window.open('/test-results', '_blank');
        }

        // Run initial tests
        window.onload = function() {
            setTimeout(runTests, 1000);
        };
    </script>
</body>
</html>
    '''
    
    return render_template_string(html_template, 
                                target_server=TARGET_SERVER,
                                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "DA-KI Test Dashboard",
        "port": 8055,
        "timestamp": datetime.now().isoformat(),
        "uptime": "active"
    })

@app.route('/api/run-tests')
def run_tests_api():
    """API endpoint to run comprehensive tests"""
    results = run_comprehensive_tests()
    return jsonify(results)

@app.route('/test-results')
def test_results():
    """Return test results as JSON"""
    results = run_comprehensive_tests()
    return jsonify(results)

if __name__ == '__main__':
    print("🔧 Starte DA-KI Test & Monitoring Dashboard...")
    print(f"📊 URL: http://{TARGET_SERVER}:8055")
    print("🎯 Test Target: 10.1.1.110")
    print("📋 Monitoring Ports: 8003 (API), 8054 (Frontend), 8055 (Test)")
    app.run(debug=False, host='0.0.0.0', port=8055)