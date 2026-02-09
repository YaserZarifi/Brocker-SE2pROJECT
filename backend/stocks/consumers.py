"""
WebSocket consumer for real-time stock price updates.
Sprint 5 - Live stock price broadcasting.

All clients join a shared group "stock_prices". When a stock price changes
(after an order match), the new price data is broadcast to all connected
clients in real-time.

This is a public endpoint - no authentication required.
"""

import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer

logger = logging.getLogger(__name__)


class StockPriceConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for broadcasting stock price updates.

    Connection (no auth required):
        ws://host/ws/stocks/

    Messages sent to client (JSON):
        {
            "type": "stock_update",
            "data": {
                "symbol": "FOLD",
                "currentPrice": 12500.0,
                "previousClose": 12300.0,
                "change": 200.0,
                "changePercent": 1.63,
                "volume": 54321,
                "high24h": 12700.0,
                "low24h": 12100.0
            }
        }
    """

    GROUP_NAME = "stock_prices"

    async def connect(self):
        # All clients join the same stock_prices group (public)
        await self.channel_layer.group_add(self.GROUP_NAME, self.channel_name)
        await self.accept()
        logger.info("WebSocket stock prices connected: channel=%s", self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP_NAME, self.channel_name)
        logger.info(
            "WebSocket stock prices disconnected: channel=%s", self.channel_name
        )

    async def receive_json(self, content, **kwargs):
        """Client-to-server messages (not used)."""
        pass

    # --- Group message handlers ---

    async def stock_price_update(self, event):
        """
        Handle a stock price update broadcast from the channel layer.

        Called when channel layer sends:
            {
                "type": "stock.price.update",
                "data": { ... stock price payload ... }
            }
        """
        await self.send_json(
            {
                "type": "stock_update",
                "data": event["data"],
            }
        )
