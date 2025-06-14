#!/bin/bash

# Aktienanalyse Web App Startup Script
# Starts all services in the correct order

set -e

echo "🚀 Starting Aktienanalyse Web App..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./install.sh first."
    exit 1
fi

# Function to check if a port is in use
check_port() {
    if lsof -i:$1 >/dev/null 2>&1; then
        echo "⚠️  Port $1 is already in use. Please stop the existing service or change the port."
        return 1
    fi
    return 0
}

# Function to start a service in background
start_service() {
    local service_name=$1
    local script_path=$2
    local port=$3
    local log_file="logs/${service_name}.log"
    
    echo "📡 Starting ${service_name} on port ${port}..."
    
    # Create logs directory if it doesn't exist
    mkdir -p logs
    
    # Start the service
    ./venv/bin/python ${script_path} > ${log_file} 2>&1 &
    local pid=$!
    
    # Store PID for cleanup
    echo $pid > "logs/${service_name}.pid"
    
    # Wait a moment and check if process is still running
    sleep 2
    if kill -0 $pid 2>/dev/null; then
        echo "✅ ${service_name} started successfully (PID: $pid)"
    else
        echo "❌ Failed to start ${service_name}. Check ${log_file} for details."
        return 1
    fi
}

# Check ports
echo "🔍 Checking ports..."
check_port 8002 || exit 1
check_port 8003 || exit 1
check_port 8054 || exit 1

# Create logs directory
mkdir -p logs

# Start services in order
start_service "search-api" "api/google_search_api.py" 8002
sleep 3

start_service "main-api" "api/api_top10_final.py" 8003
sleep 3

start_service "dashboard" "frontend/dashboard_top10.py" 8054

echo ""
echo "🎉 All services started successfully!"
echo ""
echo "📋 Service URLs:"
echo "   Dashboard:     http://localhost:8054"
echo "   Main API:      http://localhost:8003"
echo "   Search API:    http://localhost:8002"
echo ""
echo "📄 Logs are available in the 'logs/' directory"
echo "🛑 To stop all services, run: ./stop.sh"
echo ""
echo "✨ Aktienanalyse Web App is ready!"