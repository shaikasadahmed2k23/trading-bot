"""
Flask API Server for Binance Futures Trading Bot

Provides REST API endpoints to place orders, get account info, and manage trades.
Connects the web frontend with the trading bot backend.

Usage:
    python api.py
    # Server runs on http://localhost:5000
"""

from __future__ import annotations

import json
import os
from typing import Any

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from bot.client import BinanceClient, BinanceClientError
from bot.logging_config import setup_logger
from bot.orders import place_order, place_stop_market_order
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_all,
)

# ── Setup ──────────────────────────────────────────────────────────────────────
load_dotenv()
logger = setup_logger("trading_bot.api")

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# ── Global client (initialized on first request) ──────────────────────────────
_client: BinanceClient | None = None


def _get_client() -> BinanceClient:
    """Lazy-load the Binance client from environment variables."""
    global _client
    if _client is not None:
        return _client

    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        raise ValueError(
            "API credentials not configured. "
            "Please set BINANCE_API_KEY and BINANCE_API_SECRET in .env"
        )

    _client = BinanceClient(api_key=api_key, api_secret=api_secret)
    return _client


# ── Error handlers ─────────────────────────────────────────────────────────────

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"success": False, "error": "Bad request"}), 400


@app.errorhandler(500)
def internal_error(error):
    return (
        jsonify({"success": False, "error": "Internal server error"}),
        500,
    )


# ── Health Check ───────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "message": "Trading Bot API is running",
    }), 200


# ── Order Placement Endpoints ──────────────────────────────────────────────────

@app.route("/api/orders/place", methods=["POST"])
def place_order_endpoint():
    """
    Place a new order (MARKET, LIMIT, or STOP_MARKET).

    Request body:
    {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "MARKET",
        "quantity": 0.001,
        "price": null,          # Required for LIMIT, optional for others
        "stopPrice": null       # Required for STOP_MARKET
    }

    Response:
    {
        "success": true,
        "orderId": 12345,
        "clientOrderId": "...",
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "MARKET",
        "status": "FILLED",
        "origQty": "0.001",
        "executedQty": "0.001",
        "avgPrice": "43250.50"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body must be JSON",
            }), 400

        # Extract parameters
        symbol = data.get("symbol", "").strip().upper()
        side = data.get("side", "").strip().upper()
        order_type = data.get("type", "").strip().upper()
        quantity = data.get("quantity")
        price = data.get("price")
        stop_price = data.get("stopPrice")

        # Validate required fields
        if not symbol or not side or not order_type or quantity is None:
            return jsonify({
                "success": False,
                "error": "Missing required fields: symbol, side, type, quantity",
            }), 400

        logger.info(
            "API place order request: symbol=%s side=%s type=%s qty=%s",
            symbol, side, order_type, quantity,
        )

        client = _get_client()

        # Handle STOP_MARKET separately (it uses stop_price instead of price)
        if order_type == "STOP_MARKET":
            if stop_price is None:
                return jsonify({
                    "success": False,
                    "error": "STOP_MARKET orders require 'stopPrice'",
                }), 400

            try:
                # Use the place_stop_market_order function from bot.orders
                success = place_stop_market_order(
                    client=client,
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    stop_price=stop_price,
                )
                if not success:
                    return jsonify({
                        "success": False,
                        "error": "Failed to place STOP_MARKET order",
                    }), 400
            except BinanceClientError as exc:
                logger.error("Binance error: [%s] %s", exc.code, exc.message)
                return jsonify({
                    "success": False,
                    "error": f"Binance API error [{exc.code}]: {exc.message}",
                }), 400
            except Exception as exc:
                logger.error("Unexpected error: %s", exc)
                return jsonify({
                    "success": False,
                    "error": f"Error: {str(exc)}",
                }), 500

            # Return success for STOP_MARKET
            return jsonify({
                "success": True,
                "message": "STOP_MARKET order placed successfully",
                "type": "STOP_MARKET",
            }), 200

        # For MARKET and LIMIT orders
        try:
            success = place_order(
                client=client,
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
            )
            if not success:
                return jsonify({
                    "success": False,
                    "error": "Failed to place order",
                }), 400
        except BinanceClientError as exc:
            logger.error("Binance error: [%s] %s", exc.code, exc.message)
            return jsonify({
                "success": False,
                "error": f"Binance API error [{exc.code}]: {exc.message}",
            }), 400
        except Exception as exc:
            logger.error("Unexpected error: %s", exc)
            return jsonify({
                "success": False,
                "error": f"Error: {str(exc)}",
            }), 500

        return jsonify({
            "success": True,
            "message": "Order placed successfully",
            "type": order_type,
        }), 200

    except Exception as exc:
        logger.exception("Unhandled error in place_order_endpoint: %s", exc)
        return jsonify({
            "success": False,
            "error": f"Server error: {str(exc)}",
        }), 500


# ── Account Information Endpoint ───────────────────────────────────────────────

@app.route("/api/account", methods=["GET"])
def get_account():
    """
    Get account information from Binance (balance, trading status, etc.).

    Response:
    {
        "success": true,
        "accountData": { ... }
    }
    """
    try:
        client = _get_client()
        account_data = client.get_account_info()

        logger.info("Account info retrieved successfully")
        return jsonify({
            "success": True,
            "accountData": account_data,
        }), 200

    except BinanceClientError as exc:
        logger.error("Binance error: [%s] %s", exc.code, exc.message)
        return jsonify({
            "success": False,
            "error": f"Binance API error [{exc.code}]: {exc.message}",
        }), 400
    except Exception as exc:
        logger.error("Unexpected error: %s", exc)
        return jsonify({
            "success": False,
            "error": f"Error: {str(exc)}",
        }), 500


# ── Validation Endpoints ───────────────────────────────────────────────────────

@app.route("/api/validate/symbol", methods=["POST"])
def validate_symbol_endpoint():
    """Validate a trading symbol."""
    try:
        data = request.get_json()
        symbol = data.get("symbol", "").strip().upper()

        if not symbol:
            return jsonify({
                "valid": False,
                "error": "Symbol is required",
            }), 400

        try:
            validated = validate_symbol(symbol)
            return jsonify({
                "valid": True,
                "symbol": validated,
            }), 200
        except ValueError as exc:
            return jsonify({
                "valid": False,
                "error": str(exc),
            }), 400
    except Exception as exc:
        logger.error("Validation error: %s", exc)
        return jsonify({
            "valid": False,
            "error": str(exc),
        }), 500


# ── Startup Message ───────────────────────────────────────────────────────────

@app.before_request
def log_request():
    """Log incoming requests."""
    logger.debug(
        "Incoming %s request to %s",
        request.method,
        request.path,
    )


if __name__ == "__main__":
    logger.info("Starting Binance Trading Bot API server on http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
