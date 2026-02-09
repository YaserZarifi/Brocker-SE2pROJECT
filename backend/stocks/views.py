from django.db.models import Sum
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import PriceHistory, Stock
from .serializers import (
    MarketStatsSerializer,
    PriceHistorySerializer,
    StockAdminSerializer,
    StockSerializer,
)


class StockListView(generics.ListAPIView):
    """List all active stocks."""

    queryset = Stock.objects.filter(is_active=True)
    serializer_class = StockSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ["sector"]
    search_fields = ["symbol", "name", "name_fa"]
    ordering_fields = ["symbol", "current_price", "change_percent", "volume", "market_cap"]
    pagination_class = None  # Return all stocks without pagination


class StockDetailView(generics.RetrieveAPIView):
    """Get a single stock by symbol."""

    queryset = Stock.objects.filter(is_active=True)
    serializer_class = StockSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "symbol"


class StockPriceHistoryView(generics.ListAPIView):
    """Get price history for a stock."""

    serializer_class = PriceHistorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        symbol = self.kwargs["symbol"]
        days = int(self.request.query_params.get("days", 30))
        return PriceHistory.objects.filter(stock__symbol=symbol).order_by("timestamp")[:days]


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def market_stats(request):
    """Get market-level statistics."""
    stocks = Stock.objects.filter(is_active=True)
    total_stocks = stocks.count()

    aggregated = stocks.aggregate(
        total_volume=Sum("volume"),
        total_market_cap=Sum("market_cap"),
    )

    gainers = stocks.filter(change__gt=0).count()
    losers = stocks.filter(change__lt=0).count()
    unchanged = stocks.filter(change=0).count()

    # Simple index calculation: average of all stock prices weighted by market cap
    total_market_cap = aggregated["total_market_cap"] or 0
    index_value = total_market_cap / total_stocks if total_stocks > 0 else 0

    data = {
        "totalStocks": total_stocks,
        "totalVolume": aggregated["total_volume"] or 0,
        "totalMarketCap": total_market_cap,
        "gainers": gainers,
        "losers": losers,
        "unchanged": unchanged,
        "indexValue": index_value,
        "indexChange": 0,
        "indexChangePercent": 0,
    }

    return Response(data)


# ---------- Admin endpoints ----------


class AdminStockListCreateView(generics.ListCreateAPIView):
    """List or create stocks (admin only)."""

    queryset = Stock.objects.all()
    serializer_class = StockAdminSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ["sector", "is_active"]
    search_fields = ["symbol", "name", "name_fa"]


class AdminStockDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a stock (admin only)."""

    queryset = Stock.objects.all()
    serializer_class = StockAdminSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "symbol"
