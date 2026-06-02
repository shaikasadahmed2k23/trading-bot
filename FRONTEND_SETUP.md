# 🌐 Frontend Setup Guide

This guide explains how to run the web-based trading bot frontend.

## Project Structure

```
trading_bot/
├── api.py                   # Flask API server (connects backend to frontend)
├── frontend/                # Web interface (NEW)
│   ├── index.html          # Main HTML page
│   ├── styles.css          # Styling & layout
│   └── app.js              # Frontend logic & API calls
├── bot/                     # Trading bot backend modules
│   ├── client.py           # Binance API client
│   ├── orders.py           # Order placement logic
│   ├── validators.py       # Input validation
│   └── logging_config.py   # Logging setup
├── cli.py                  # Command-line interface (optional)
├── requirements.txt        # Python dependencies
└── README.md              # Original documentation
```

## How It Works

1. **Flask API Server** (`api.py`)
   - Runs on `http://localhost:5000`
   - Exposes REST API endpoints
   - Uses the existing bot modules to place orders
   - Handles validation and error responses

2. **Web Frontend** (`frontend/`)
   - Beautiful, modern UI built with HTML/CSS/JavaScript
   - No framework dependencies (vanilla JavaScript)
   - Communicates with the Flask API
   - Real-time status updates

3. **Trading Bot Backend** (`bot/`)
   - Unchanged from original
   - Handles Binance API signing, authentication, and order placement
   - Validates inputs and handles errors

---

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `requests` — HTTP client for Binance API
- `typer` — CLI framework (for cli.py)
- `python-dotenv` — Environment variable management
- `flask` — Web framework for API server (NEW)
- `flask-cors` — Cross-Origin Resource Sharing support (NEW)

### 2. Configure API Credentials

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Binance Futures Testnet credentials:

```env
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

[Get your keys at: https://testnet.binancefuture.com](https://testnet.binancefuture.com)

---

## Running the Application

### Option 1: Run the Web Frontend (Recommended)

**Terminal 1 — Start the API Server:**

```bash
python api.py
```

Expected output:
```
Starting Binance Trading Bot API server on http://localhost:5000
```

**Terminal 2 — Serve the Frontend:**

```bash
# On Windows
python -m http.server 8000 --directory frontend

# On macOS/Linux
python3 -m http.server 8000 --directory frontend
```

Expected output:
```
Serving HTTP on 0.0.0.0 port 8000 ...
```

**Then open your browser to:**

```
http://localhost:8000
```

### Option 2: Use the CLI (Original)

Still works as before:

```bash
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

---

## Frontend Features

### 📋 Order Placement
- **MARKET** orders — execute immediately at best available price
- **LIMIT** orders — execute at your specified price or better
- **STOP_MARKET** orders — trigger when price reaches a level

### ✅ Input Validation
- Real-time symbol validation
- Quantity and price checks
- Conditional fields based on order type

### 🔄 Live Status
- API connection status indicator
- Real-time server health checks
- Automatic retry on connection issues

### 💡 User-Friendly
- Modern, responsive design
- Clear error messages
- Order summary before execution
- Mobile-friendly interface

---

## API Endpoints

### Health Check
```
GET /api/health
```

### Place Order
```
POST /api/orders/place

Body:
{
  "symbol": "BTCUSDT",
  "side": "BUY",
  "type": "MARKET",
  "quantity": 0.001,
  "price": null,           // Required for LIMIT
  "stopPrice": null        // Required for STOP_MARKET
}
```

### Get Account Info
```
GET /api/account
```

### Validate Symbol
```
POST /api/validate/symbol

Body:
{
  "symbol": "BTCUSDT"
}
```

---

## Troubleshooting

### API Server Won't Start
- Ensure port 5000 is not in use: `netstat -ano | findstr :5000` (Windows)
- Check `.env` file has valid credentials
- Verify Flask is installed: `pip install flask flask-cors`

### Frontend Can't Connect to API
- Verify API server is running on `http://localhost:5000`
- Check browser console (F12) for CORS or network errors
- Ensure firewall allows localhost connections

### Orders Won't Place
- Verify Binance API credentials are correct
- Check `.env` file is in the project root
- Review logs in `logs/` folder for details
- Ensure your Binance testnet account has USDT balance

### Port Already in Use
- API (Flask): Change port in `api.py` line `app.run(port=5000)`
- Frontend: Change port in http.server command: `python -m http.server 8001`

---

## Development Notes

### Frontend Technologies
- **HTML5** — Semantic structure
- **CSS3** — Modern styling with CSS Grid & Flexbox
- **JavaScript (Vanilla)** — No frameworks, lightweight
- **Fetch API** — Async HTTP requests

### API Architecture
- **Flask** — Lightweight Python web framework
- **CORS** — Cross-origin requests support
- **Error Handling** — Comprehensive validation and error messages
- **Logging** — Built on existing logging infrastructure

### Adding Features
To extend the frontend:
1. Add new endpoints in `api.py`
2. Add form inputs in `index.html`
3. Add JavaScript handlers in `app.js`

---

## Production Deployment

For production use:
1. Set `debug=False` in `api.py`
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Serve frontend from CDN or nginx
4. Add authentication/authorization layer
5. Use HTTPS for secure API communication
6. Configure proper CORS settings

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api:app
```

---

## Support

For issues or questions:
1. Check the logs in `logs/` folder
2. Review browser console (F12)
3. Verify all dependencies are installed
4. Ensure `.env` file is properly configured
5. Test API directly: `curl http://localhost:5000/api/health`

Happy trading! 🚀
