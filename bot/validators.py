"""
Validators for all user-supplied CLI inputs.
Raises ValueError with clear messages on bad input.
"""

from __future__ import annotations

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}

# Common Binance Futures USDT-M symbols (non-exhaustive safeguard)
SYMBOL_SUFFIX = "USDT"


def validate_symbol(symbol: str) -> str:
    """
    Normalise and validate a trading symbol.
    Rules:
      - Must be non-empty
      - Converted to uppercase
      - Must end with 'USDT' (USDT-M futures)
    """
    if not symbol or not symbol.strip():
        raise ValueError("Symbol cannot be empty.")
    symbol = symbol.strip().upper()
    if not symbol.endswith(SYMBOL_SUFFIX):
        raise ValueError(
            f"Symbol '{symbol}' must end with 'USDT' for USDT-M futures "
            f"(e.g. BTCUSDT, ETHUSDT)."
        )
    return symbol


def validate_side(side: str) -> str:
    """
    Validate order side.
    Accepted values: BUY, SELL (case-insensitive).
    """
    if not side or not side.strip():
        raise ValueError("Side cannot be empty.")
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(
            f"Invalid side '{side}'. Must be one of: {', '.join(sorted(VALID_SIDES))}."
        )
    return side


def validate_order_type(order_type: str) -> str:
    """
    Validate order type.
    Accepted values: MARKET, LIMIT, STOP_MARKET (case-insensitive).
    """
    if not order_type or not order_type.strip():
        raise ValueError("Order type cannot be empty.")
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. "
            f"Must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )
    return order_type


def validate_quantity(quantity: float | str) -> float:
    """
    Validate order quantity.
    Rules:
      - Must be a positive number
      - Must be > 0
    """
    try:
        qty = float(quantity)
    except (TypeError, ValueError):
        raise ValueError(f"Quantity '{quantity}' is not a valid number.")
    if qty <= 0:
        raise ValueError(f"Quantity must be greater than 0. Got: {qty}.")
    return qty


def validate_price(price: float | str | None, order_type: str) -> float | None:
    """
    Validate price based on order type.
    Rules:
      - MARKET  : price must be None / not provided
      - LIMIT   : price is required and must be > 0
      - STOP_MARKET: price is required (used as stopPrice) and must be > 0
    """
    order_type = order_type.upper()

    if order_type == "MARKET":
        if price is not None:
            # Warn but don't block — just ignore the price
            return None
        return None

    # LIMIT and STOP_MARKET both need a price
    if price is None:
        raise ValueError(
            f"Price is required for '{order_type}' orders."
        )
    try:
        p = float(price)
    except (TypeError, ValueError):
        raise ValueError(f"Price '{price}' is not a valid number.")
    if p <= 0:
        raise ValueError(f"Price must be greater than 0. Got: {p}.")
    return p


def validate_all(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float | str,
    price: float | str | None = None,
) -> dict:
    """
    Run all validations and return a clean dict of validated values.
    Raises ValueError on the first validation failure.
    """
    v_symbol = validate_symbol(symbol)
    v_side = validate_side(side)
    v_type = validate_order_type(order_type)
    v_qty = validate_quantity(quantity)
    v_price = validate_price(price, v_type)

    return {
        "symbol": v_symbol,
        "side": v_side,
        "order_type": v_type,
        "quantity": v_qty,
        "price": v_price,
    }