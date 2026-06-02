"""
trading_bot.bot — core package

Exposes:
  - BinanceClient   : low-level REST wrapper
  - place_order     : high-level order placement with validation + output
  - setup_logger    : shared logger factory
"""

from bot.client import BinanceClient, BinanceClientError
from bot.logging_config import setup_logger
from bot.orders import place_order, place_stop_market_order

__all__ = [
    "BinanceClient",
    "BinanceClientError",
    "setup_logger",
    "place_order",
    "place_stop_market_order",
]