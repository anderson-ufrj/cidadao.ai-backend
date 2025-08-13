#!/bin/bash
# Cidadão.AI Backend - Start Script

echo "🏛️ Starting Cidadão.AI Backend..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✅ Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  No virtual environment found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Installing dependencies..."
    pip install -r requirements-hf.txt
fi

# Set environment for local development
export ENV=local

# Check if port 7860 is available
if lsof -Pi :7860 -sTCP:LISTEN -t >/dev/null ; then
    echo "❌ Port 7860 is already in use. Please stop the existing service."
    exit 1
fi

# Start the application
echo "🚀 Launching Cidadão.AI Backend..."
echo "📍 Local URL: http://localhost:7860"
echo "📍 API Docs: http://localhost:7860/docs"
echo "📍 Share URL will be displayed if enabled"
echo ""
echo "Press Ctrl+C to stop the server"

python3 app.py