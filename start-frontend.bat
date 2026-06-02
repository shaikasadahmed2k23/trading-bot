@echo off
REM Start Trading Bot - Frontend Server
REM Windows batch script to serve the frontend on port 8000

echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║  🌐  Binance Futures Trading Bot - Web Frontend                    ║
echo ║                                                                    ║
echo ║  Frontend will be available at: http://localhost:8000             ║
echo ║  Make sure API server is running on: http://localhost:5000        ║
echo ║                                                                    ║
echo ║  Press Ctrl+C to stop the server                                  ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

REM Check if frontend folder exists
if not exist frontend\ (
    echo ❌  Frontend folder not found!
    echo.
    pause
    exit /b 1
)

REM Start the HTTP server
echo Starting web server on port 8000...
echo.

python -m http.server 8000 --directory frontend

pause
