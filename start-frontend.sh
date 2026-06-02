#!/bin/bash
# Start Trading Bot - Frontend Server
# macOS/Linux shell script to serve the frontend on port 8000

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  🌐  Binance Futures Trading Bot - Web Frontend                    ║"
echo "║                                                                    ║"
echo "║  Frontend will be available at: http://localhost:8000             ║"
echo "║  Make sure API server is running on: http://localhost:5000        ║"
echo "║                                                                    ║"
echo "║  Press Ctrl+C to stop the server                                  ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if frontend folder exists
if [ ! -d "frontend" ]; then
    echo "❌  Frontend folder not found!"
    echo ""
    exit 1
fi

# Start the HTTP server
echo "Starting web server on port 8000..."
echo ""

python3 -m http.server 8000 --directory frontend
