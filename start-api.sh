#!/bin/bash
# Start Trading Bot - API Server
# macOS/Linux shell script to run the Flask API server

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  🤖  Binance Futures Trading Bot - API Server                      ║"
echo "║                                                                    ║"
echo "║  Frontend will be available at: http://localhost:8000             ║"
echo "║  API will be running on:        http://localhost:5000             ║"
echo "║                                                                    ║"
echo "║  Open another terminal and run: ./start-frontend.sh               ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo ""
    echo "Please create a .env file with your Binance API credentials:"
    echo ""
    echo "  BINANCE_API_KEY=your_api_key_here"
    echo "  BINANCE_API_SECRET=your_api_secret_here"
    echo ""
    echo "Get your keys at: https://testnet.binancefuture.com"
    echo ""
    exit 1
fi

# Check if requirements are installed
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Required packages not installed!"
    echo ""
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
    echo ""
fi

# Start the Flask API server
echo "Starting Flask API server..."
echo ""

python3 api.py
