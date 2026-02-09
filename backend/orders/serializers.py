from rest_framework import serializers

from .models import Order, PortfolioHolding


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model - maps to frontend Order interface."""

    userId = serializers.UUIDField(source="user_id", read_only=True)
    stockSymbol = serializers.CharField(source="stock.symbol", read_only=True)
    stockName = serializers.CharField(source="stock.name", read_only=True)
    filledQuantity = serializers.IntegerField(source="filled_quantity", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "userId",
            "stockSymbol",
            "stockName",
            "type",
            "price",
            "quantity",
            "filledQuantity",
            "status",
            "createdAt",
            "updatedAt",
        ]
        read_only_fields = ["id", "userId", "filledQuantity", "status", "createdAt", "updatedAt"]


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating a new order."""

    stock_symbol = serializers.CharField(max_length=10)
    type = serializers.ChoiceField(choices=Order.OrderType.choices)
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    quantity = serializers.IntegerField(min_value=1)


class PortfolioHoldingSerializer(serializers.ModelSerializer):
    """Serializer for PortfolioHolding - maps to frontend PortfolioHolding interface."""

    stockSymbol = serializers.CharField(source="stock.symbol", read_only=True)
    stockName = serializers.CharField(source="stock.name", read_only=True)
    stockNameFa = serializers.CharField(source="stock.name_fa", read_only=True)
    averageBuyPrice = serializers.DecimalField(source="average_buy_price", max_digits=12, decimal_places=2, read_only=True)
    currentPrice = serializers.SerializerMethodField()
    totalValue = serializers.SerializerMethodField()
    profitLoss = serializers.SerializerMethodField()
    profitLossPercent = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioHolding
        fields = [
            "stockSymbol",
            "stockName",
            "stockNameFa",
            "quantity",
            "averageBuyPrice",
            "currentPrice",
            "totalValue",
            "profitLoss",
            "profitLossPercent",
        ]

    def get_currentPrice(self, obj):
        return float(obj.current_price)

    def get_totalValue(self, obj):
        return float(obj.total_value)

    def get_profitLoss(self, obj):
        return float(obj.profit_loss)

    def get_profitLossPercent(self, obj):
        return round(float(obj.profit_loss_percent), 2)


class PortfolioSerializer(serializers.Serializer):
    """Serializer for full portfolio - maps to frontend Portfolio interface."""

    userId = serializers.UUIDField()
    holdings = PortfolioHoldingSerializer(many=True)
    totalValue = serializers.DecimalField(max_digits=15, decimal_places=2)
    totalInvested = serializers.DecimalField(max_digits=15, decimal_places=2)
    totalProfitLoss = serializers.DecimalField(max_digits=15, decimal_places=2)
    totalProfitLossPercent = serializers.DecimalField(max_digits=8, decimal_places=2)
    cashBalance = serializers.DecimalField(max_digits=15, decimal_places=2)


class OrderBookEntrySerializer(serializers.Serializer):
    """Serializer for an order book entry."""

    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    quantity = serializers.IntegerField()
    total = serializers.DecimalField(max_digits=15, decimal_places=2)
    count = serializers.IntegerField()


class OrderBookSerializer(serializers.Serializer):
    """Serializer for order book - maps to frontend OrderBook interface."""

    symbol = serializers.CharField()
    bids = OrderBookEntrySerializer(many=True)
    asks = OrderBookEntrySerializer(many=True)
    spread = serializers.DecimalField(max_digits=12, decimal_places=2)
    spreadPercent = serializers.DecimalField(max_digits=8, decimal_places=4)
