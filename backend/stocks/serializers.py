from rest_framework import serializers

from .models import PriceHistory, Stock


class StockSerializer(serializers.ModelSerializer):
    """Serializer for Stock model - maps to frontend Stock interface."""

    # Frontend uses camelCase; DRF uses snake_case by default
    nameFa = serializers.CharField(source="name_fa")
    currentPrice = serializers.DecimalField(source="current_price", max_digits=12, decimal_places=2)
    previousClose = serializers.DecimalField(source="previous_close", max_digits=12, decimal_places=2)
    changePercent = serializers.DecimalField(source="change_percent", max_digits=8, decimal_places=4)
    marketCap = serializers.IntegerField(source="market_cap")
    high24h = serializers.DecimalField(source="high_24h", max_digits=12, decimal_places=2)
    low24h = serializers.DecimalField(source="low_24h", max_digits=12, decimal_places=2)
    open = serializers.DecimalField(source="open_price", max_digits=12, decimal_places=2)
    sectorFa = serializers.CharField(source="sector_fa")

    class Meta:
        model = Stock
        fields = [
            "symbol",
            "name",
            "nameFa",
            "currentPrice",
            "previousClose",
            "change",
            "changePercent",
            "volume",
            "marketCap",
            "high24h",
            "low24h",
            "open",
            "sector",
            "sectorFa",
            "logo",
        ]


class StockAdminSerializer(serializers.ModelSerializer):
    """Serializer for admin stock management (snake_case + all fields)."""

    class Meta:
        model = Stock
        fields = "__all__"


class PriceHistorySerializer(serializers.ModelSerializer):
    """Serializer for PriceHistory model - maps to frontend PriceHistory interface."""

    open = serializers.DecimalField(source="open_price", max_digits=12, decimal_places=2)

    class Meta:
        model = PriceHistory
        fields = ["timestamp", "open", "high", "low", "close", "volume"]


class MarketStatsSerializer(serializers.Serializer):
    """Serializer for market-level statistics."""

    totalStocks = serializers.IntegerField()
    totalVolume = serializers.IntegerField()
    totalMarketCap = serializers.IntegerField()
    gainers = serializers.IntegerField()
    losers = serializers.IntegerField()
    unchanged = serializers.IntegerField()
    indexValue = serializers.DecimalField(max_digits=15, decimal_places=2)
    indexChange = serializers.DecimalField(max_digits=15, decimal_places=2)
    indexChangePercent = serializers.DecimalField(max_digits=8, decimal_places=4)
