"""
Order views for BourseChain.
Sprint 3 - Updated with cash/stock reservation, matching engine trigger, cancel refund.
"""

import logging
from decimal import Decimal

from django.db import transaction as db_transaction
from django.db.models import F, Sum
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

logger = logging.getLogger(__name__)


class OrderListView(generics.ListAPIView):
    """List all orders for the authenticated user."""

    serializer_class = OrderSerializer
    filterset_fields = ["type", "status"]
    ordering_fields = ["created_at", "price", "quantity"]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related("stock")


class OrderCreateView(generics.CreateAPIView):
    """
    Create a new order with cash/stock reservation.

    Buy orders: cash is reserved (deducted from balance immediately).
    Sell orders: stock is reserved (deducted from holdings immediately).

    After creation, the matching engine is triggered asynchronously via Celery.
    """

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

        if data["type"] == "buy":
            order, error = self._create_buy_order(user, stock, data)
        else:
            order, error = self._create_sell_order(user, stock, data)

        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        # Trigger matching engine asynchronously via Celery
        self._trigger_matching(order)

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )

    @db_transaction.atomic
    def _create_buy_order(self, user, stock, data):
        """
        Create a buy order and reserve cash.
        Returns (order, None) on success or (None, error_message) on failure.
        """
        total_cost = data["price"] * data["quantity"]

        # Lock user row for update to prevent race conditions
        user = type(user).objects.select_for_update().get(pk=user.pk)

        if user.cash_balance < total_cost:
            return None, "Insufficient cash balance."

        # Reserve cash: deduct from balance
        user.cash_balance -= total_cost
        user.save(update_fields=["cash_balance"])

        order = Order.objects.create(
            user=user,
            stock=stock,
            type=data["type"],
            price=data["price"],
            quantity=data["quantity"],
        )

        logger.info(
            f"Buy order created: {order.id} - {data['quantity']} {stock.symbol} "
            f"@ {data['price']} (reserved {total_cost} cash)"
        )

        return order, None

    @db_transaction.atomic
    def _create_sell_order(self, user, stock, data):
        """
        Create a sell order and reserve stock.
        Returns (order, None) on success or (None, error_message) on failure.
        """
        # Lock holding row for update to prevent race conditions
        holding = (
            PortfolioHolding.objects.select_for_update()
            .filter(user=user, stock=stock)
            .first()
        )

        if not holding or holding.quantity < data["quantity"]:
            return None, "Insufficient stock holdings."

        # Reserve stock: deduct from holdings
        holding.quantity -= data["quantity"]
        holding.save(update_fields=["quantity"])

        order = Order.objects.create(
            user=user,
            stock=stock,
            type=data["type"],
            price=data["price"],
            quantity=data["quantity"],
        )

        logger.info(
            f"Sell order created: {order.id} - {data['quantity']} {stock.symbol} "
            f"@ {data['price']} (reserved {data['quantity']} shares)"
        )

        return order, None

    def _trigger_matching(self, order):
        """Trigger the matching engine via Celery task."""
        from .tasks import match_order_task

        try:
            match_order_task.delay(str(order.id))
            logger.info(f"Matching task queued for order {order.id}")
        except Exception as e:
            logger.error(f"Failed to queue matching task for order {order.id}: {e}")
            # Fallback: try synchronous matching if Celery is unavailable
            try:
                from .matching import match_order

                match_order(str(order.id))
                logger.info(f"Fallback: synchronous matching for order {order.id}")
            except Exception as e2:
                logger.error(f"Synchronous matching also failed: {e2}")


class OrderDetailView(generics.RetrieveAPIView):
    """Get a single order."""

    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related("stock")


class OrderCancelView(generics.UpdateAPIView):
    """
    Cancel a pending/partial order and refund reserved cash/stock.

    Buy orders: refund remaining unreserved cash.
    Sell orders: return reserved shares to portfolio.
    """

    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user,
            status__in=[Order.OrderStatus.PENDING, Order.OrderStatus.PARTIAL],
        )

    @db_transaction.atomic
    def update(self, request, *args, **kwargs):
        order = self.get_object()
        remaining_qty = order.quantity - order.filled_quantity

        if remaining_qty > 0:
            if order.type == Order.OrderType.BUY:
                # Refund reserved cash for unfilled portion
                refund_amount = order.price * remaining_qty
                user = type(order.user).objects.select_for_update().get(pk=order.user.pk)
                user.cash_balance += refund_amount
                user.save(update_fields=["cash_balance"])
                logger.info(
                    f"Order {order.id} cancelled: refunded {refund_amount} cash"
                )

            elif order.type == Order.OrderType.SELL:
                # Return reserved shares to portfolio
                holding, _ = PortfolioHolding.objects.select_for_update().get_or_create(
                    user=order.user,
                    stock=order.stock,
                    defaults={"quantity": 0, "average_buy_price": Decimal("0")},
                )
                holding.quantity += remaining_qty
                holding.save(update_fields=["quantity"])
                logger.info(
                    f"Order {order.id} cancelled: returned {remaining_qty} shares"
                )

        # Update order status
        if order.filled_quantity > 0:
            # Partially filled order: keep the filled portion as matched
            order.status = Order.OrderStatus.CANCELLED
        else:
            order.status = Order.OrderStatus.CANCELLED

        order.save(update_fields=["status", "updated_at"])

        return Response(OrderSerializer(order).data)


@api_view(["GET"])
def portfolio_view(request):
    """Get the authenticated user's portfolio."""
    user = request.user
    holdings = PortfolioHolding.objects.filter(
        user=user, quantity__gt=0
    ).select_related("stock")

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
    """
    Get the order book for a stock.
    Shows remaining (unfilled) quantities for pending/partial orders.
    """
    try:
        stock = Stock.objects.get(symbol=symbol, is_active=True)
    except Stock.DoesNotExist:
        return Response(
            {"error": "Stock not found."}, status=status.HTTP_404_NOT_FOUND
        )

    # Annotate remaining quantity (quantity - filled_quantity)
    base_qs = Order.objects.filter(
        stock=stock, status__in=["pending", "partial"]
    ).annotate(remaining=F("quantity") - F("filled_quantity"))

    # Aggregate buy orders (bids) - remaining quantities
    buy_orders = (
        base_qs.filter(type="buy")
        .values("price")
        .annotate(total_quantity=Sum("remaining"))
        .order_by("-price")[:10]
    )

    # Aggregate sell orders (asks) - remaining quantities
    sell_orders = (
        base_qs.filter(type="sell")
        .values("price")
        .annotate(total_quantity=Sum("remaining"))
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
