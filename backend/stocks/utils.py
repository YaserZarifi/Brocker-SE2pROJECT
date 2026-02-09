"""
Utility functions for broadcasting stock price updates via WebSocket.
Sprint 5 - Real-time stock price push.

Called from the matching engine (orders/matching.py) after updating
stock prices, to push live data to all connected WebSocket clients.
"""

import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


def broadcast_stock_price(stock):
    """
    Broadcast updated stock price to all WebSocket clients.

    Args:
        stock: Stock model instance with updated price data
    """
    try:
        channel_layer = get_channel_layer()
        if channel_layer is None:
            logger.debug("No channel layer available, skipping stock WS broadcast")
            return

        # Serialize stock data (matching frontend Stock interface - camelCase)
        data = {
            "symbol": stock.symbol,
            "name": stock.name,
            "nameFa": stock.name_fa,
            "currentPrice": float(stock.current_price),
            "previousClose": float(stock.previous_close),
            "change": float(stock.change),
            "changePercent": float(stock.change_percent),
            "volume": stock.volume,
            "high24h": float(stock.high_24h),
            "low24h": float(stock.low_24h),
        }

        async_to_sync(channel_layer.group_send)(
            "stock_prices",
            {
                "type": "stock.price.update",
                "data": data,
            },
        )
        logger.info(
            "Broadcast stock price update: %s @ %s",
            stock.symbol,
            stock.current_price,
        )
    except Exception as e:
        # Never let WebSocket broadcasting break the main flow
        logger.warning("Failed to broadcast stock price via WebSocket: %s", e)
