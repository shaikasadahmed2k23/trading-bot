@echo off
REM Start Trading Bot - API Server
REM Windows batch script to run the Flask API server

echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║  🤖  Binance Futures Trading Bot - API Server                      ║
echo ║                                                                    ║
echo ║  Frontend will be available at: http://localhost:8000             ║
echo ║  API will be running on:        http://localhost:5000             ║
echo ║                                                                    ║
echo ║  Open another terminal and run: start-frontend.bat                ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found!
    echo.
    echo Please create a .env file with your Binance API credentials:
    echo.
    echo   BINANCE_API_KEY=your_api_key_here
    echo   BINANCE_API_SECRET=your_api_secret_here
    echo.
    echo Get your keys at: https://testnet.binancefuture.com
    echo.
    pause
    exit /b 1
)

REM Check if requirements are installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Required packages not installed!
    echo.
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Start the Flask API server
echo Starting Flask API server...
echo.

python api.py

pause
