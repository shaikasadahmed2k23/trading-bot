"""
Binance Futures Testnet — low-level REST client.

Handles:
  - HMAC-SHA256 request signing
  - Timestamping
  - HTTP GET / POST with error handling
  - Logging of every request and response
"""

from __future__ import annotations

import hashlib
import hmac
import time
import urllib.parse
from typing import Any

import requests

from bot.logging_config import setup_logger

# ── Constants ─────────────────────────────────────────────────────────────────
BASE_URL = "https://testnet.binancefuture.com"
RECV_WINDOW = 5000          # ms — how long a signed request stays valid
REQUEST_TIMEOUT = 10        # seconds

logger = setup_logger("trading_bot.client")


class BinanceClientError(Exception):
    """Raised when Binance returns a non-2xx response or an error payload."""

    def __init__(self, code: int | str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance API Error [{code}]: {message}")


class BinanceClient:
    """
    Thin wrapper around the Binance Futures Testnet REST API.

    Usage
    -----
    client = BinanceClient(api_key="...", api_secret="...")
    response = client.place_order(symbol="BTCUSDT", side="BUY",
                                  order_type="MARKET", quantity=0.001)
    """

    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            raise ValueError("Both API key and API secret are required.")
        self._api_key = api_key
        self._api_secret = api_secret
        self._session = requests.Session()
        self._session.headers.update(
            {
                "X-MBX-APIKEY": self._api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        logger.info("BinanceClient initialised (testnet: %s)", BASE_URL)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _timestamp(self) -> int:
        """Current UTC timestamp in milliseconds."""
        return int(time.time() * 1000)

    def _sign(self, params: dict) -> dict:
        """
        Add 'timestamp', 'recvWindow', and 'signature' to params dict.
        Signature = HMAC-SHA256 of the query string.
        """
        params["timestamp"] = self._timestamp()
        params["recvWindow"] = RECV_WINDOW
        query_string = urllib.parse.urlencode(params)
        signature = hmac.new(
            self._api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _handle_response(self, response: requests.Response) -> dict:
        """
        Parse JSON response.
        Raises BinanceClientError for API-level errors.
        Raises requests.HTTPError for HTTP-level errors.
        """
        logger.debug(
            "HTTP %s %s | body: %s",
            response.status_code,
            response.url,
            response.text[:500],   # truncate long responses in logs
        )

        try:
            data: Any = response.json()
        except ValueError:
            response.raise_for_status()
            return {}

        # Binance error format: {"code": -XXXX, "msg": "..."}
        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            raise BinanceClientError(
                code=data.get("code", "unknown"),
                message=data.get("msg", "Unknown error"),
            )

        response.raise_for_status()
        return data

    def _post(self, endpoint: str, params: dict) -> dict:
        """Sign and POST to a private endpoint."""
        signed_params = self._sign(params)
        url = BASE_URL + endpoint
        logger.debug("POST %s | params: %s", url, {k: v for k, v in signed_params.items() if k != "signature"})

        try:
            response = self._session.post(
                url,
                data=signed_params,
                timeout=REQUEST_TIMEOUT,
            )
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error connecting to Binance: %s", exc)
            raise ConnectionError(
                "Cannot reach Binance Futures Testnet. Check your internet connection."
            ) from exc
        except requests.exceptions.Timeout as exc:
            logger.error("Request timed out: %s", exc)
            raise TimeoutError(
                f"Request timed out after {REQUEST_TIMEOUT}s."
            ) from exc

        return self._handle_response(response)

    def _get(self, endpoint: str, params: dict | None = None) -> dict:
        """GET a public or private endpoint (unsigned)."""
        url = BASE_URL + endpoint
        logger.debug("GET %s | params: %s", url, params)
        try:
            response = self._session.get(
                url,
                params=params or {},
                timeout=REQUEST_TIMEOUT,
            )
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error: %s", exc)
            raise ConnectionError(
                "Cannot reach Binance Futures Testnet."
            ) from exc
        return self._handle_response(response)

    # ── Public API methods ────────────────────────────────────────────────────

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float | None = None,
        stop_price: float | None = None,
        time_in_force: str = "GTC",
    ) -> dict:
        """
        Place a new order on Binance Futures Testnet.

        Parameters
        ----------
        symbol      : e.g. "BTCUSDT"
        side        : "BUY" or "SELL"
        order_type  : "MARKET", "LIMIT", or "STOP_MARKET"
        quantity    : order size in base asset
        price       : required for LIMIT orders
        stop_price  : required for STOP_MARKET orders
        time_in_force: "GTC" (default) | "IOC" | "FOK"  — LIMIT orders only
        """
        params: dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            if price is None:
                raise ValueError("Price is required for LIMIT orders.")
            params["price"] = price
            params["timeInForce"] = time_in_force

        elif order_type == "STOP_MARKET":
            if stop_price is None:
                raise ValueError("stopPrice is required for STOP_MARKET orders.")
            params["stopPrice"] = stop_price

        logger.info(
            "Placing order → symbol=%s | side=%s | type=%s | qty=%s | price=%s | stopPrice=%s",
            symbol, side, order_type, quantity, price, stop_price,
        )

        result = self._post("/fapi/v1/order", params)
        logger.info("Order placed successfully | orderId=%s | status=%s", result.get("orderId"), result.get("status"))
        return result

    def get_account_info(self) -> dict:
        """Fetch account balance and position info."""
        params: dict = {}
        signed = self._sign(params)
        url = BASE_URL + "/fapi/v2/account"
        logger.debug("GET account info")
        try:
            response = self._session.get(url, params=signed, timeout=REQUEST_TIMEOUT)
        except requests.exceptions.ConnectionError as exc:
            raise ConnectionError("Cannot reach Binance Futures Testnet.") from exc
        return self._handle_response(response)

    def get_exchange_info(self, symbol: str | None = None) -> dict:
        """Fetch exchange info (symbols, filters, precision)."""
        params = {"symbol": symbol} if symbol else {}
        return self._get("/fapi/v1/exchangeInfo", params)