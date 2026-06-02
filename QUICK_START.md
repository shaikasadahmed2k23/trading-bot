# ⚡ Quick Reference Guide

## 🚀 Start the App (30 seconds)

### Windows
```bash
# Terminal 1
start-api.bat

# Terminal 2
start-frontend.bat

# Open browser
http://localhost:8000
```

### macOS/Linux
```bash
# Terminal 1
./start-api.sh

# Terminal 2
./start-frontend.sh

# Open browser
http://localhost:8000
```

---

## 📋 What You Get

### Web Frontend
- Modern, responsive trading interface
- MARKET, LIMIT, STOP_MARKET orders
- Real-time API status
- Mobile-friendly

### API Server
- RESTful endpoints
- Order placement
- Account info
- Health checks

### CLI (Still Available)
```bash
# Direct order
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# Interactive mode
python cli.py interactive

# Account info
python cli.py account
```

---

## 🔧 Setup (First Time)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
cp .env.example .env

# 3. Add credentials (edit .env)
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret

# 4. Run the app
# Follow "Start the App" section above
```

---

## 📍 URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:8000 | Trading UI |
| API | http://localhost:5000 | REST API |
| API Health | http://localhost:5000/api/health | Status check |

---

## 🔌 API Endpoints

```bash
# Health check
curl http://localhost:5000/api/health

# Place order
curl -X POST http://localhost:5000/api/orders/place \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "MARKET",
    "quantity": 0.001
  }'

# Account info
curl http://localhost:5000/api/account

# Validate symbol
curl -X POST http://localhost:5000/api/validate/symbol \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT"}'
```

---

## 📁 File Structure

```
trading_bot/
├── 🆕 api.py                    # Flask API server
├── 🆕 frontend/                 # Web interface
│   ├── index.html              # HTML page
│   ├── styles.css              # Styling
│   └── app.js                  # JavaScript logic
├── 🆕 start-api.bat/sh          # Run API server
├── 🆕 start-frontend.bat/sh     # Run frontend
├── 🆕 FRONTEND_SETUP.md         # Detailed guide
├── 🆕 INTEGRATION_SUMMARY.md    # What was added
├── bot/                         # Trading bot (unchanged)
├── cli.py                       # CLI interface
├── requirements.txt             # Dependencies
└── README.md                    # Main documentation
```

---

## ⚠️ Before You Start

1. ✅ Install Python 3.7+
2. ✅ Have Binance API keys ready (testnet)
3. ✅ Create `.env` file with credentials
4. ✅ Run `pip install -r requirements.txt`
5. ✅ Ensure ports 5000 & 8000 are free

---

## 🎯 Common Tasks

### Place a Market Order
1. Open http://localhost:8000
2. Fill form:
   - Symbol: BTCUSDT
   - Side: BUY
   - Type: MARKET
   - Quantity: 0.001
3. Click "Place Order"

### Place a Limit Order
1. Open http://localhost:8000
2. Fill form:
   - Symbol: BTCUSDT
   - Side: BUY
   - Type: LIMIT
   - Quantity: 0.001
   - Price: 60000
3. Click "Place Order"

### Check API Status
```bash
curl http://localhost:5000/api/health
```

### View Logs
```bash
cat logs/trading_bot_*.log  # macOS/Linux
type logs/trading_bot_*.log # Windows
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| API won't start | Check port 5000 is free, install Flask |
| Can't connect to API | Verify Flask running, check localhost:5000 |
| Orders fail | Check .env credentials, verify testnet balance |
| Port already in use | Change port in `api.py` or stop other services |
| Frontend shows "Offline" | Start API server first, check localhost:5000 |

---

## 📚 More Info

- **FRONTEND_SETUP.md** — Full frontend guide
- **INTEGRATION_SUMMARY.md** — Architecture & details
- **README.md** — Complete documentation
- **logs/** — Application logs

---

## 🚀 Deploy to Production

```bash
# Install production server
pip install gunicorn

# Run API server
gunicorn -w 4 -b 0.0.0.0:5000 api:app

# Serve frontend via nginx or CDN
```

---

## 💡 Pro Tips

- 🔄 API auto-checks health every 5 seconds
- 📝 All orders logged to `logs/trading_bot_*.log`
- 🌐 Frontend works offline (will retry when online)
- 💰 Always use testnet first!
- 🔐 Never commit `.env` with real keys

---

## ✨ Features at a Glance

✅ MARKET orders
✅ LIMIT orders  
✅ STOP_MARKET orders
✅ Input validation
✅ Real-time status
✅ Modern responsive UI
✅ REST API
✅ CLI interface
✅ Full error handling
✅ Structured logging

Happy trading! 🎉
