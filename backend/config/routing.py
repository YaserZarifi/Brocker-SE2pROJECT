"""
WebSocket URL routing for BourseChain.
Sprint 5 - Real-time notifications + stock price updates.

Routes:
  ws://host/ws/notifications/  → NotificationConsumer (auth required)
  ws://host/ws/stocks/         → StockPriceConsumer (public)
"""

from django.urls import path

from notifications.consumers import NotificationConsumer
from stocks.consumers import StockPriceConsumer

websocket_urlpatterns = [
    path("ws/notifications/", NotificationConsumer.as_asgi()),
    path("ws/stocks/", StockPriceConsumer.as_asgi()),
]
