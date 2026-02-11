from datetime import datetime, timedelta
from decimal import Decimal

from django.db.models import Sum
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import PriceHistory, Stock

# Interval config: (limit_days, points_to_return, intraday_candles_per_day)
INTERVAL_CONFIG = {
    "1m": (1, 60, 60 * 24),
    "5m": (1, 72, 12 * 24),
    "15m": (3, 96, 4 * 24),
    "1h": (7, 168, 24),
    "4h": (14, 42, 6),
    "1D": (30, 30, 1),
    "1W": (90, 12, 0),  # 0 = aggregate weekly
}
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


def _synthesize_intraday(daily_records, candles_per_day):
    """Generate intraday OHLC candles from daily data."""
    result = []
    for rec in daily_records:
        o, h, l, c = float(rec.open_price), float(rec.high), float(rec.low), float(rec.close)
        base_ts = datetime.combine(rec.timestamp, datetime.min.time())
        vol_per = rec.volume // candles_per_day if candles_per_day else 0

        for i in range(candles_per_day):
            t = i / candles_per_day
            # Simple interpolation
            price = o + (c - o) * t + (h - max(o, c)) * (0.5 - abs(t - 0.5) * 2)
            p2 = o + (c - o) * ((i + 1) / candles_per_day)
            ts = base_ts + timedelta(hours=24 * i / candles_per_day)
            result.append({
                "timestamp": ts.isoformat(),
                "open": round(price, 2),
                "high": round(max(price, p2) * 1.002, 2),
                "low": round(min(price, p2) * 0.998, 2),
                "close": round(p2, 2),
                "volume": vol_per,
            })
    return result


def _aggregate_weekly(daily_records):
    """Aggregate daily OHLC into weekly candles."""
    from collections import defaultdict

    by_week = defaultdict(list)
    for rec in daily_records:
        dt = rec.timestamp
        week_key = (dt.year, dt.isocalendar()[1])
        by_week[week_key].append(rec)

    result = []
    for (y, w), recs in sorted(by_week.items()):
        recs_sorted = sorted(recs, key=lambda r: r.timestamp)
        o = float(recs_sorted[0].open_price)
        c = float(recs_sorted[-1].close)
        h = max(float(r.high) for r in recs_sorted)
        low = min(float(r.low) for r in recs_sorted)
        vol = sum(r.volume for r in recs_sorted)
        ts = recs_sorted[0].timestamp
        result.append({
            "timestamp": datetime.combine(ts, datetime.min.time()).isoformat(),
            "open": o, "high": h, "low": low, "close": c, "volume": vol,
        })
    return result[-12:]  # last 12 weeks


class StockPriceHistoryView(generics.ListAPIView):
    """Get price history for a stock. Supports interval: 1m, 5m, 15m, 1h, 4h, 1D, 1W."""

    serializer_class = PriceHistorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def list(self, request, *args, **kwargs):
        symbol = kwargs["symbol"]
        interval = request.query_params.get("interval", "1D")
        days = int(request.query_params.get("days", 30))

        config = INTERVAL_CONFIG.get(interval, INTERVAL_CONFIG["1D"])
        limit_days, max_points, intraday = config

        qs = (
            PriceHistory.objects.filter(stock__symbol=symbol)
            .order_by("timestamp")[: limit_days * 2 if intraday else limit_days + 14]
        )
        records = list(qs)

        if intraday == 0 and interval == "1W":
            data = _aggregate_weekly(records)
        elif intraday > 1:
            data = _synthesize_intraday(records[:limit_days], min(intraday, 24 * 60))
            data = data[-max_points:]
        elif intraday == 1:
            # Daily - use as-is
            data = [
                {
                    "timestamp": datetime.combine(r.timestamp, datetime.min.time()).isoformat(),
                    "open": float(r.open_price),
                    "high": float(r.high),
                    "low": float(r.low),
                    "close": float(r.close),
                    "volume": r.volume,
                }
                for r in records[:max_points]
            ]
        else:
            data = [
                {
                    "timestamp": datetime.combine(r.timestamp, datetime.min.time()).isoformat(),
                    "open": float(r.open_price),
                    "high": float(r.high),
                    "low": float(r.low),
                    "close": float(r.close),
                    "volume": r.volume,
                }
                for r in records[:max_points]
            ]

        return Response(data)


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
