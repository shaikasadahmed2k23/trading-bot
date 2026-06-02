"""
Order placement logic and response formatting.

This layer sits between the CLI and the BinanceClient.
It:
  - validates inputs
  - calls the client
  - formats and prints order summaries
  - handles and logs errors gracefully
"""

from __future__ import annotations

import json

from bot.client import BinanceClient, BinanceClientError
from bot.logging_config import setup_logger
from bot.validators import validate_all

logger = setup_logger("trading_bot.orders")


# ── Pretty-print helpers ───────────────────────────────────────────────────────

def _divider(char: str = "─", width: int = 52) -> str:
    return char * width


def _print_request_summary(params: dict) -> None:
    print()
    print(_divider("═"))
    print("  📋  ORDER REQUEST SUMMARY")
    print(_divider())
    print(f"  Symbol     : {params['symbol']}")
    print(f"  Side       : {params['side']}")
    print(f"  Order Type : {params['order_type']}")
    print(f"  Quantity   : {params['quantity']}")
    if params.get("price"):
        print(f"  Price      : {params['price']}")
    print(_divider())


def _print_order_response(response: dict) -> None:
    print()
    print("  ✅  ORDER RESPONSE")
    print(_divider())
    print(f"  Order ID      : {response.get('orderId', 'N/A')}")
    print(f"  Client OID    : {response.get('clientOrderId', 'N/A')}")
    print(f"  Symbol        : {response.get('symbol', 'N/A')}")
    print(f"  Side          : {response.get('side', 'N/A')}")
    print(f"  Type          : {response.get('type', 'N/A')}")
    print(f"  Status        : {response.get('status', 'N/A')}")
    print(f"  Quantity      : {response.get('origQty', 'N/A')}")
    print(f"  Executed Qty  : {response.get('executedQty', 'N/A')}")

    avg_price = response.get("avgPrice") or response.get("price") or "N/A"
    print(f"  Avg Price     : {avg_price}")

    if response.get("stopPrice") and response["stopPrice"] != "0":
        print(f"  Stop Price    : {response['stopPrice']}")

    print(_divider("═"))
    print()


def _print_error(message: str) -> None:
    print()
    print(_divider("═"))
    print("  ❌  ORDER FAILED")
    print(_divider())
    print(f"  Reason : {message}")
    print(_divider("═"))
    print()


# ── Core order functions ───────────────────────────────────────────────────────

def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float | str,
    price: float | str | None = None,
) -> bool:
    """
    Validate inputs, place the order, and print results.

    Returns True on success, False on failure.
    """
    # ── 1. Validate inputs ────────────────────────────────────────────────────
    try:
        validated = validate_all(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
        )
    except ValueError as exc:
        logger.warning("Validation failed: %s", exc)
        _print_error(f"Validation Error — {exc}")
        return False

    # ── 2. Print request summary ──────────────────────────────────────────────
    _print_request_summary(validated)

    # ── 3. Place order via client ─────────────────────────────────────────────
    try:
        response = client.place_order(
            symbol=validated["symbol"],
            side=validated["side"],
            order_type=validated["order_type"],
            quantity=validated["quantity"],
            price=validated["price"],
        )
    except BinanceClientError as exc:
        logger.error("Binance API error: [%s] %s", exc.code, exc.message)
        _print_error(f"API Error [{exc.code}] — {exc.message}")
        return False
    except (ConnectionError, TimeoutError) as exc:
        logger.error("Network error: %s", exc)
        _print_error(f"Network Error — {exc}")
        return False
    except Exception as exc:
        logger.exception("Unexpected error during order placement: %s", exc)
        _print_error(f"Unexpected Error — {exc}")
        return False

    # ── 4. Log full response ──────────────────────────────────────────────────
    logger.debug("Full order response: %s", json.dumps(response, indent=2))

    # ── 5. Print response and success message ─────────────────────────────────
    _print_order_response(response)
    print("  🎉  Order placed successfully on Binance Futures Testnet!")
    print()
    return True


def place_stop_market_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float | str,
    stop_price: float | str,
) -> bool:
    """
    Place a STOP_MARKET order (bonus order type).

    A stop-market triggers a market order when price hits `stop_price`.
    """
    # Validate base fields
    try:
        v_symbol = __import__("bot.validators", fromlist=["validate_symbol"]).validate_symbol(symbol)
        v_side   = __import__("bot.validators", fromlist=["validate_side"]).validate_side(side)
        v_qty    = __import__("bot.validators", fromlist=["validate_quantity"]).validate_quantity(quantity)
        v_stop   = __import__("bot.validators", fromlist=["validate_price"]).validate_price(stop_price, "STOP_MARKET")
    except ValueError as exc:
        logger.warning("Validation failed: %s", exc)
        _print_error(f"Validation Error — {exc}")
        return False

    summary = {
        "symbol": v_symbol,
        "side": v_side,
        "order_type": "STOP_MARKET",
        "quantity": v_qty,
        "price": f"Stop @ {v_stop}",
    }
    _print_request_summary(summary)

    try:
        response = client.place_order(
            symbol=v_symbol,
            side=v_side,
            order_type="STOP_MARKET",
            quantity=v_qty,
            stop_price=v_stop,
        )
    except BinanceClientError as exc:
        logger.error("Binance API error: [%s] %s", exc.code, exc.message)
        _print_error(f"API Error [{exc.code}] — {exc.message}")
        return False
    except (ConnectionError, TimeoutError) as exc:
        logger.error("Network error: %s", exc)
        _print_error(f"Network Error — {exc}")
        return False
    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)
        _print_error(f"Unexpected Error — {exc}")
        return False

    logger.debug("Full stop-market response: %s", json.dumps(response, indent=2))
    _print_order_response(response)
    print("  🎉  Stop-Market order placed successfully!")
    print()
    return True