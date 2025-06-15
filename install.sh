#!/bin/bash

# Aktienanalyse Web App Installation Script
# This script sets up the German stock analysis web application

set -e  # Exit on any error

echo "🚀 Installing Aktienanalyse Web App..."

# Check if Python 3.11+ is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Make scripts executable
chmod +x start.sh 2>/dev/null || true

echo "✅ Installation completed successfully!"
echo ""
echo "🎯 Next steps:"
echo "1. Run './start.sh' to start all services"
echo "2. Access the dashboard at http://10.1.1.110:8054"
echo "3. API will be available at http://10.1.1.110:8003"
echo ""
echo "📋 Individual service commands:"
echo "   API Server:    ./venv/bin/python api/api_top10_final.py"
echo "   Search API:    ./venv/bin/python api/google_search_api.py"
echo "   Dashboard:     ./venv/bin/python frontend/dashboard_top10.py"