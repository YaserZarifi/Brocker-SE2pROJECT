"""
BourseChain URL Configuration
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health_check(request):
    """Simple health check endpoint for Docker/K8s probes."""
    return JsonResponse({"status": "ok", "service": "boursechain-backend"})


urlpatterns = [
    # Health check (Sprint 6: Docker/K8s readiness probe)
    path("health/", health_check, name="health-check"),
    # Prometheus metrics (Sprint 6: Monitoring)
    path("", include("django_prometheus.urls")),
    # Admin
    path("admin/", admin.site.urls),
    # API v1
    path("api/v1/auth/", include("users.urls")),
    path("api/v1/stocks/", include("stocks.urls")),
    path("api/v1/orders/", include("orders.urls")),
    path("api/v1/transactions/", include("transactions.urls")),
    path("api/v1/notifications/", include("notifications.urls")),
    path("api/v1/blockchain/", include("blockchain_service.urls")),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
