"""
JWT Authentication Middleware for Django Channels WebSocket connections.
Sprint 5 - Real-time WebSocket

WebSocket connections cannot use HTTP headers for authentication, so we
pass the JWT access token as a query parameter:
    ws://host/ws/notifications/?token=<jwt-access-token>

This middleware extracts and validates the token, setting scope["user"]
to the authenticated user (or AnonymousUser if invalid/missing).
"""

import logging
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken

logger = logging.getLogger(__name__)
User = get_user_model()


@database_sync_to_async
def get_user_from_token(token_str):
    """Validate a JWT access token and return the corresponding user."""
    try:
        token = AccessToken(token_str)
        user_id = token["user_id"]
        return User.objects.get(id=user_id)
    except Exception as e:
        logger.debug("WebSocket JWT auth failed: %s", e)
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom middleware that reads a JWT token from the WebSocket
    query string and authenticates the user.

    Usage in ASGI routing:
        JWTAuthMiddleware(URLRouter(websocket_urlpatterns))

    Client connects with:
        new WebSocket("ws://host/ws/path/?token=<jwt>")
    """

    async def __call__(self, scope, receive, send):
        # Parse query string for token
        query_string = scope.get("query_string", b"").decode("utf-8")
        query_params = parse_qs(query_string)
        token_list = query_params.get("token", [])

        if token_list:
            scope["user"] = await get_user_from_token(token_list[0])
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
