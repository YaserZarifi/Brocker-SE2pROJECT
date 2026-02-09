"""
ASGI config for BourseChain project.
Sprint 5 - Supports HTTP and WebSocket (Django Channels).

The application routes:
  - HTTP requests → Django ASGI handler (normal REST API)
  - WebSocket requests (/ws/...) → Channels consumers
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that would otherwise fail.
django_asgi_app = get_asgi_application()

# Import after Django setup
from config.ws_auth import JWTAuthMiddleware  # noqa: E402
from config.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        ),
    }
)
