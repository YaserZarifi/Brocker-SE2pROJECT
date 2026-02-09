from decimal import Decimal

from django.db.models import Sum
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from stocks.models import Stock

from .models import Order, PortfolioHolding
from .serializers import (
    OrderBookSerializer,
    OrderCreateSerializer,
    OrderSerializer,
    PortfolioHoldingSerializer,
    PortfolioSerializer,
)


class OrderListView(generics.ListAPIView):
    """List all orders for the authenticated user."""

    serializer_class = OrderSerializer
    filterset_fields = ["type", "status"]
    ordering_fields = ["created_at", "price", "quantity"]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related("stock")


class OrderCreateView(generics.CreateAPIView):
    """Create a new order."""

    serializer_class = OrderCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        try:
            stock = Stock.objects.get(symbol=data["stock_symbol"], is_active=True)
        except Stock.DoesNotExist:
            return Response(
                {"error": "Stock not found or inactive."},
                status=status.HTTP_404_NOT_FOUND,
            )

        user = request.user

        # Validation for buy orders: check cash balance
        if data["type"] == "buy":
            total_cost = data["price"] * data["quantity"]
            if user.cash_balance < total_cost:
                return Response(
                    {"error": "Insufficient cash balance."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Validation for sell orders: check holdings
        if data["type"] == "sell":
            holding = PortfolioHolding.objects.filter(user=user, stock=stock).first()
            if not holding or holding.quantity < data["quantity"]:
                return Response(
                    {"error": "Insufficient stock holdings."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        order = Order.objects.create(
            user=user,
            stock=stock,
            type=data["type"],
            price=data["price"],
            quantity=data["quantity"],
        )

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )


class OrderDetailView(generics.RetrieveAPIView):
    """Get a single order."""

    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related("stock")


class OrderCancelView(generics.UpdateAPIView):
    """Cancel a pending order."""

    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, status=Order.OrderStatus.PENDING)

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        order.status = Order.OrderStatus.CANCELLED
        order.save(update_fields=["status", "updated_at"])
        return Response(OrderSerializer(order).data)


@api_view(["GET"])
def portfolio_view(request):
    """Get the authenticated user's portfolio."""
    user = request.user
    holdings = PortfolioHolding.objects.filter(user=user, quantity__gt=0).select_related("stock")

    holdings_data = PortfolioHoldingSerializer(holdings, many=True).data

    total_value = sum(h.total_value for h in holdings)
    total_invested = sum(h.total_invested for h in holdings)
    total_pl = total_value - total_invested
    total_pl_percent = (total_pl / total_invested * 100) if total_invested > 0 else 0

    portfolio_data = {
        "userId": str(user.id),
        "holdings": holdings_data,
        "totalValue": float(total_value),
        "totalInvested": float(total_invested),
        "totalProfitLoss": float(total_pl),
        "totalProfitLossPercent": round(float(total_pl_percent), 2),
        "cashBalance": float(user.cash_balance),
    }

    return Response(portfolio_data)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def order_book_view(request, symbol):
    """Get the order book for a stock."""
    try:
        stock = Stock.objects.get(symbol=symbol, is_active=True)
    except Stock.DoesNotExist:
        return Response({"error": "Stock not found."}, status=status.HTTP_404_NOT_FOUND)

    # Aggregate buy orders (bids)
    buy_orders = (
        Order.objects.filter(stock=stock, type="buy", status__in=["pending", "partial"])
        .values("price")
        .annotate(total_quantity=Sum("quantity"), order_count=Sum("quantity"))
        .order_by("-price")[:10]
    )

    # Aggregate sell orders (asks)
    sell_orders = (
        Order.objects.filter(stock=stock, type="sell", status__in=["pending", "partial"])
        .values("price")
        .annotate(total_quantity=Sum("quantity"), order_count=Sum("quantity"))
        .order_by("price")[:10]
    )

    bids = [
        {
            "price": float(o["price"]),
            "quantity": o["total_quantity"],
            "total": float(o["price"]) * o["total_quantity"],
            "count": 1,
        }
        for o in buy_orders
    ]

    asks = [
        {
            "price": float(o["price"]),
            "quantity": o["total_quantity"],
            "total": float(o["price"]) * o["total_quantity"],
            "count": 1,
        }
        for o in sell_orders
    ]

    best_bid = bids[0]["price"] if bids else 0
    best_ask = asks[0]["price"] if asks else 0
    spread = best_ask - best_bid if (best_ask and best_bid) else 0
    spread_pct = (spread / best_ask * 100) if best_ask > 0 else 0

    data = {
        "symbol": symbol,
        "bids": bids,
        "asks": asks,
        "spread": round(spread, 2),
        "spreadPercent": round(spread_pct, 4),
    }

    return Response(data)
