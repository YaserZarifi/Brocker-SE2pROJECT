from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model - maps to frontend Transaction interface."""

    buyOrderId = serializers.UUIDField(source="buy_order_id", read_only=True)
    sellOrderId = serializers.UUIDField(source="sell_order_id", read_only=True)
    stockSymbol = serializers.CharField(source="stock.symbol", read_only=True)
    stockName = serializers.CharField(source="stock.name", read_only=True)
    totalValue = serializers.DecimalField(source="total_value", max_digits=15, decimal_places=2, read_only=True)
    buyerId = serializers.UUIDField(source="buyer_id", read_only=True)
    sellerId = serializers.UUIDField(source="seller_id", read_only=True)
    blockchainHash = serializers.CharField(source="blockchain_hash", read_only=True, allow_null=True)
    executedAt = serializers.DateTimeField(source="executed_at", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "buyOrderId",
            "sellOrderId",
            "stockSymbol",
            "stockName",
            "price",
            "quantity",
            "totalValue",
            "buyerId",
            "sellerId",
            "blockchainHash",
            "executedAt",
            "status",
        ]
