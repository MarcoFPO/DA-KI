#!/bin/bash

# Aktienanalyse Web App Stop Script
# Stops all running services

echo "🛑 Stopping Aktienanalyse Web App services..."

# Function to stop a service
stop_service() {
    local service_name=$1
    local pid_file="logs/${service_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "🔄 Stopping ${service_name} (PID: $pid)..."
            kill "$pid"
            sleep 2
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo "⚡ Force stopping ${service_name}..."
                kill -9 "$pid"
            fi
            
            echo "✅ ${service_name} stopped"
        else
            echo "ℹ️  ${service_name} was not running"
        fi
        rm -f "$pid_file"
    else
        echo "ℹ️  No PID file found for ${service_name}"
    fi
}

# Stop services
stop_service "dashboard"
stop_service "main-api"
stop_service "search-api"

# Clean up any remaining processes on the ports
echo "🧹 Cleaning up any remaining processes..."
for port in 8002 8003 8054; do
    pid=$(lsof -ti:$port 2>/dev/null || true)
    if [ ! -z "$pid" ]; then
        echo "🔧 Killing process on port $port (PID: $pid)..."
        kill -9 $pid 2>/dev/null || true
    fi
done

echo ""
echo "✅ All services stopped successfully!"