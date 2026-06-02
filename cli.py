"""
cli.py — Trading Bot CLI Entry Point

Enhanced CLI using Typer with:
  - Direct command mode  (pass all args via flags)
  - Interactive mode     (guided prompts if no args given)
  - Clear validation messages at every step
  - Rich output formatting

Usage examples:
  python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
  python cli.py place --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 80000
  python cli.py place --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.01 --stop-price 75000
  python cli.py interactive
  python cli.py account
"""

from __future__ import annotations

import os
import sys
from typing import Optional

import typer
from dotenv import load_dotenv

from bot.client import BinanceClient, BinanceClientError
from bot.logging_config import setup_logger
from bot.orders import place_order, place_stop_market_order
from bot.validators import (
    VALID_SIDES,
    VALID_ORDER_TYPES,
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
)

# ── Setup ──────────────────────────────────────────────────────────────────────
load_dotenv()
logger = setup_logger("trading_bot.cli")

app = typer.Typer(
    name="trading-bot",
    help="🤖  Binance Futures Testnet Trading Bot — place MARKET, LIMIT & STOP_MARKET orders.",
    add_completion=False,
    rich_markup_mode="markdown",
)

BANNER = """
╔══════════════════════════════════════════════════════╗
║       🤖  Binance Futures Testnet Trading Bot        ║
║              USDT-M Perpetual Futures                ║
╚══════════════════════════════════════════════════════╝
"""


# ── Shared client factory ──────────────────────────────────────────────────────

def _get_client() -> BinanceClient:
    """
    Load API credentials from environment variables and return a BinanceClient.
    Exits with a friendly message if credentials are missing.
    """
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        typer.echo()
        typer.echo("  ⚠️   API credentials not found!")
        typer.echo()
        typer.echo("  Please create a .env file in the project root:")
        typer.echo("    BINANCE_API_KEY=your_api_key_here")
        typer.echo("    BINANCE_API_SECRET=your_api_secret_here")
        typer.echo()
        typer.echo("  Get your keys at: https://testnet.binancefuture.com")
        typer.echo()
        raise typer.Exit(code=1)

    return BinanceClient(api_key=api_key, api_secret=api_secret)


# ── Prompt helpers (for interactive mode) ─────────────────────────────────────

def _prompt_with_validation(prompt_text: str, validator, *args) -> str:
    """Loop until the user enters a valid value."""
    while True:
        value = typer.prompt(prompt_text).strip()
        try:
            result = validator(value, *args) if args else validator(value)
            return result
        except ValueError as exc:
            typer.echo(f"  ⚠️   {exc} Please try again.")


def _prompt_optional_float(prompt_text: str) -> Optional[float]:
    """Prompt for an optional float. Returns None if user presses Enter."""
    value = typer.prompt(prompt_text, default="").strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        typer.echo("  ⚠️   Invalid number. Treating as not provided.")
        return None


# ── Commands ───────────────────────────────────────────────────────────────────

@app.command()
def place(
    symbol: str = typer.Option(
        ...,
        "--symbol", "-s",
        help="Trading pair symbol, e.g. BTCUSDT",
        prompt="Symbol (e.g. BTCUSDT)",
    ),
    side: str = typer.Option(
        ...,
        "--side",
        help="Order side: BUY or SELL",
        prompt="Side (BUY/SELL)",
    ),
    order_type: str = typer.Option(
        ...,
        "--type", "-t",
        help="Order type: MARKET | LIMIT | STOP_MARKET",
        prompt="Order type (MARKET/LIMIT/STOP_MARKET)",
    ),
    quantity: float = typer.Option(
        ...,
        "--quantity", "-q",
        help="Order quantity in base asset (e.g. 0.001 for BTC)",
        prompt="Quantity",
    ),
    price: Optional[float] = typer.Option(
        None,
        "--price", "-p",
        help="Limit price — required for LIMIT orders",
    ),
    stop_price: Optional[float] = typer.Option(
        None,
        "--stop-price",
        help="Stop trigger price — required for STOP_MARKET orders",
    ),
):
    """
    **Place a single order** on Binance Futures Testnet.

    Examples:

    \b
    # Market buy
    python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

    \b
    # Limit sell
    python cli.py place --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 80000

    \b
    # Stop-market sell (bonus order type)
    python cli.py place --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 75000
    """
    typer.echo(BANNER)
    logger.info(
        "CLI place command → symbol=%s side=%s type=%s qty=%s price=%s stop=%s",
        symbol, side, order_type, quantity, price, stop_price,
    )

    client = _get_client()
    order_type_upper = order_type.strip().upper()

    if order_type_upper == "STOP_MARKET":
        if stop_price is None:
            stop_price = typer.prompt("Stop Price (trigger price)", type=float)
        success = place_stop_market_order(
            client=client,
            symbol=symbol,
            side=side,
            quantity=quantity,
            stop_price=stop_price,
        )
    else:
        success = place_order(
            client=client,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
        )

    raise typer.Exit(code=0 if success else 1)


@app.command()
def interactive():
    """
    **Interactive mode** — guided prompts to build and place an order step by step.

    Great for first-time users or when you prefer menus over flags.
    """
    typer.echo(BANNER)
    typer.echo("  Welcome to Interactive Mode! Answer the prompts below.\n")

    client = _get_client()

    # ── Step 1: Symbol ────────────────────────────────────────────────────────
    typer.echo("  Step 1/5 — Trading Symbol")
    typer.echo("  Examples: BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT")
    symbol = _prompt_with_validation("  Symbol", validate_symbol)

    # ── Step 2: Side ──────────────────────────────────────────────────────────
    typer.echo()
    typer.echo("  Step 2/5 — Order Side")
    typer.echo("  [1] BUY   [2] SELL")
    side_input = typer.prompt("  Enter side (BUY/SELL)").strip().upper()
    # Allow numeric shortcut
    if side_input == "1":
        side_input = "BUY"
    elif side_input == "2":
        side_input = "SELL"
    try:
        side = validate_side(side_input)
    except ValueError as exc:
        typer.echo(f"  ⚠️  {exc}")
        raise typer.Exit(code=1)

    # ── Step 3: Order Type ────────────────────────────────────────────────────
    typer.echo()
    typer.echo("  Step 3/5 — Order Type")
    typer.echo("  [1] MARKET      — executes immediately at best available price")
    typer.echo("  [2] LIMIT       — executes at your specified price or better")
    typer.echo("  [3] STOP_MARKET — triggers a market order at your stop price  ⭐ bonus")
    type_input = typer.prompt("  Enter order type (MARKET/LIMIT/STOP_MARKET or 1/2/3)").strip().upper()
    type_map = {"1": "MARKET", "2": "LIMIT", "3": "STOP_MARKET"}
    type_input = type_map.get(type_input, type_input)
    try:
        order_type = validate_order_type(type_input)
    except ValueError as exc:
        typer.echo(f"  ⚠️  {exc}")
        raise typer.Exit(code=1)

    # ── Step 4: Quantity ──────────────────────────────────────────────────────
    typer.echo()
    typer.echo("  Step 4/5 — Quantity")
    typer.echo("  Enter the amount in base asset (e.g. 0.001 for 0.001 BTC)")
    quantity = _prompt_with_validation("  Quantity", validate_quantity)

    # ── Step 5: Price (conditional) ───────────────────────────────────────────
    price = None
    stop_price = None

    if order_type == "LIMIT":
        typer.echo()
        typer.echo("  Step 5/5 — Limit Price")
        price = _prompt_with_validation("  Limit Price (USDT)", validate_price, order_type)

    elif order_type == "STOP_MARKET":
        typer.echo()
        typer.echo("  Step 5/5 — Stop Trigger Price")
        typer.echo("  The order will trigger a market order when price reaches this level.")
        stop_price = _prompt_with_validation("  Stop Price (USDT)", validate_price, order_type)
    else:
        typer.echo()
        typer.echo("  Step 5/5 — Price")
        typer.echo("  MARKET order — no price needed. ✓")

    # ── Confirm ───────────────────────────────────────────────────────────────
    typer.echo()
    typer.echo("  ─────────────────────────────────────────────")
    typer.echo("  Confirm order:")
    typer.echo(f"    {side} {quantity} {symbol} @ {order_type}", )
    if price:
        typer.echo(f"    Price      : {price}")
    if stop_price:
        typer.echo(f"    Stop Price : {stop_price}")
    typer.echo("  ─────────────────────────────────────────────")

    confirm = typer.confirm("\n  Place this order?", default=True)
    if not confirm:
        typer.echo("  Order cancelled.")
        raise typer.Exit()

    # ── Place ─────────────────────────────────────────────────────────────────
    if order_type == "STOP_MARKET":
        success = place_stop_market_order(
            client=client,
            symbol=symbol,
            side=side,
            quantity=float(quantity),
            stop_price=float(stop_price),
        )
    else:
        success = place_order(
            client=client,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=float(quantity),
            price=float(price) if price else None,
        )

    raise typer.Exit(code=0 if success else 1)


@app.command()
def account():
    """
    **Show account info** — balances and positions from Binance Futures Testnet.
    """
    typer.echo(BANNER)
    client = _get_client()

    typer.echo("  Fetching account info...\n")
    try:
        info = client.get_account_info()
    except BinanceClientError as exc:
        typer.echo(f"  ❌  API Error [{exc.code}]: {exc.message}")
        raise typer.Exit(code=1)
    except (ConnectionError, TimeoutError) as exc:
        typer.echo(f"  ❌  Network Error: {exc}")
        raise typer.Exit(code=1)

    typer.echo("  ══════════════════════════════════════════════════")
    typer.echo("  ACCOUNT BALANCES (non-zero)")
    typer.echo("  ──────────────────────────────────────────────────")
    assets = info.get("assets", [])
    shown = 0
    for asset in assets:
        balance = float(asset.get("walletBalance", 0))
        if balance > 0:
            typer.echo(
                f"  {asset['asset']:<8}  Wallet: {balance:.4f}  "
                f"Unrealised PnL: {float(asset.get('unrealizedProfit', 0)):.4f}"
            )
            shown += 1
    if shown == 0:
        typer.echo("  No non-zero balances found.")

    positions = [p for p in info.get("positions", []) if float(p.get("positionAmt", 0)) != 0]
    if positions:
        typer.echo()
        typer.echo("  OPEN POSITIONS")
        typer.echo("  ──────────────────────────────────────────────────")
        for pos in positions:
            typer.echo(
                f"  {pos['symbol']:<12}  Amt: {pos['positionAmt']}  "
                f"Entry: {pos.get('entryPrice', 'N/A')}  "
                f"PnL: {float(pos.get('unrealizedProfit', 0)):.4f}"
            )
    typer.echo("  ══════════════════════════════════════════════════\n")


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app()