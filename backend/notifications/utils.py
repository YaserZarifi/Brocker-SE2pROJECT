"""
Utility functions for broadcasting notifications via WebSocket.
Sprint 5 - Real-time notification push.

These functions are called from the matching engine (orders/matching.py)
after creating Notification objects, to push them to connected WebSocket
clients in real-time.
"""

import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


def broadcast_notification(notification):
    """
    Broadcast a notification to the user's WebSocket group.

    Args:
        notification: Notification model instance (already saved to DB)
    """
    try:
        channel_layer = get_channel_layer()
        if channel_layer is None:
            logger.debug("No channel layer available, skipping WS broadcast")
            return

        group_name = f"notifications_{notification.user_id}"

        # Serialize notification data (matching frontend Notification interface)
        data = {
            "id": str(notification.id),
            "userId": str(notification.user_id),
            "title": notification.title,
            "titleFa": notification.title_fa,
            "message": notification.message,
            "messageFa": notification.message_fa,
            "type": notification.type,
            "read": notification.read,
            "createdAt": notification.created_at.isoformat(),
        }

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "notification.message",
                "data": data,
            },
        )
        logger.info(
            "Broadcast notification to %s: %s", group_name, notification.title
        )
    except Exception as e:
        # Never let WebSocket broadcasting break the main flow
        logger.warning("Failed to broadcast notification via WebSocket: %s", e)
