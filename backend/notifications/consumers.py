"""
WebSocket consumer for real-time notifications.
Sprint 5 - Push notifications via WebSocket.

Each authenticated user joins a personal group: "notifications_{user_id}"
When a notification is created (e.g. after order match), it is broadcast
to the user's group and pushed to their WebSocket connection in real-time.
"""

import json
import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for user-specific real-time notifications.

    Requires JWT authentication via query parameter:
        ws://host/ws/notifications/?token=<jwt-access-token>

    Messages sent to client (JSON):
        {
            "type": "notification",
            "data": {
                "id": "uuid",
                "title": "...",
                "titleFa": "...",
                "message": "...",
                "messageFa": "...",
                "type": "order_matched",
                "read": false,
                "createdAt": "ISO datetime"
            }
        }
    """

    async def connect(self):
        self.user = self.scope.get("user", AnonymousUser())

        if isinstance(self.user, AnonymousUser) or not self.user.is_authenticated:
            logger.info("WebSocket notification connection rejected: unauthenticated")
            await self.close()
            return

        # Join user-specific notification group
        self.group_name = f"notifications_{self.user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info(
            "WebSocket notification connected: user=%s group=%s",
            self.user.email,
            self.group_name,
        )

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name, self.channel_name
            )
            logger.info(
                "WebSocket notification disconnected: user=%s",
                getattr(self.user, "email", "unknown"),
            )

    async def receive_json(self, content, **kwargs):
        """Client-to-server messages (currently not used, but could be for acks)."""
        pass

    # --- Group message handlers ---

    async def notification_message(self, event):
        """
        Handle a notification broadcast from the channel layer.

        Called when channel layer sends:
            {
                "type": "notification.message",
                "data": { ... notification payload ... }
            }
        """
        await self.send_json(
            {
                "type": "notification",
                "data": event["data"],
            }
        )
