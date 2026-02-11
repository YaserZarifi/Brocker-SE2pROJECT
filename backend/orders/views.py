"""
Order views for BourseChain.
Sprint 3 - Updated with cash/stock reservation, matching engine trigger, cancel refund.
Binance-style: Market, Limit, Stop-Loss, Take-Profit order types.
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


def _get_order_book_prices(stock):
    """Get best bid and best ask for a stock from the order book."""
    base_qs = Order.objects.filter(
        stock=stock,
        status__in=[Order.OrderStatus.PENDING, Order.OrderStatus.PARTIAL],
    ).annotate(remaining=F("quantity") - F("filled_quantity"))

    best_ask = (
        base_qs.filter(type=Order.OrderType.SELL)
        .values("price")
        .order_by("price")
        .first()
    )
    best_bid = (
        base_qs.filter(type=Order.OrderType.BUY)
        .values("price")
        .order_by("-price")
        .first()
    )
    return (
        Decimal(str(best_ask["price"])) if best_ask else None,
        Decimal(str(best_bid["price"])) if best_bid else None,
    )
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
        execution_type = data.get("execution_type", Order.ExecutionType.LIMIT)

        # Stop-Loss / Take-Profit: create as pending conditional order (triggered later)
        if execution_type in (
            Order.ExecutionType.STOP_LOSS,
            Order.ExecutionType.TAKE_PROFIT,
        ):
            order, error = self._create_conditional_order(user, stock, data)
        elif data["type"] == "buy":
            order, error = self._create_buy_order(user, stock, data)
        else:
            order, error = self._create_sell_order(user, stock, data)

        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        self._trigger_matching(order)

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )

    @db_transaction.atomic
    def _create_buy_order(self, user, stock, data):
        """
        Create a buy order and reserve cash.
        - Limit: reserve price * quantity
        - Market: reserve best_ask * quantity (or current_price if no asks)
        """
        execution_type = data.get("execution_type", Order.ExecutionType.LIMIT)
        if execution_type == Order.ExecutionType.MARKET:
            best_ask, _ = _get_order_book_prices(stock)
            price = best_ask if best_ask is not None else stock.current_price
            if price <= 0:
                return None, "No liquidity available for market buy."
            data = {**data, "price": price}
        else:
            price = data["price"]

        total_cost = price * data["quantity"]

        user = type(user).objects.select_for_update().get(pk=user.pk)
        if user.cash_balance < total_cost:
            return None, "Insufficient cash balance."

        user.cash_balance -= total_cost
        user.save(update_fields=["cash_balance"])

        order = Order.objects.create(
            user=user,
            stock=stock,
            type=data["type"],
            execution_type=execution_type,
            price=price,
            quantity=data["quantity"],
        )

        logger.info(
            f"Buy order created: {order.id} - {data['quantity']} {stock.symbol} "
            f"@ {price} ({execution_type})"
        )
        return order, None

    @db_transaction.atomic
    def _create_sell_order(self, user, stock, data):
        """
        Create a sell order and reserve stock.
        - Limit: price from data
        - Market: price = best_bid or current_price (for display/reservation ref)
        """
        execution_type = data.get("execution_type", Order.ExecutionType.LIMIT)
        if execution_type == Order.ExecutionType.MARKET:
            _, best_bid = _get_order_book_prices(stock)
            price = best_bid if best_bid is not None else stock.current_price
            if price <= 0:
                return None, "No liquidity available for market sell."
            data = {**data, "price": price}
        else:
            price = data["price"]

        holding = (
            PortfolioHolding.objects.select_for_update()
            .filter(user=user, stock=stock)
            .first()
        )
        if not holding or holding.quantity < data["quantity"]:
            return None, "Insufficient stock holdings."

        holding.quantity -= data["quantity"]
        holding.save(update_fields=["quantity"])

        order = Order.objects.create(
            user=user,
            stock=stock,
            type=data["type"],
            execution_type=execution_type,
            price=price,
            quantity=data["quantity"],
        )

        logger.info(
            f"Sell order created: {order.id} - {data['quantity']} {stock.symbol} "
            f"@ {price} ({execution_type})"
        )
        return order, None

    def _create_conditional_order(self, user, stock, data):
        """Create Stop-Loss or Take-Profit order (stays pending until trigger)."""
        order = Order.objects.create(
            user=user,
            stock=stock,
            type=data["type"],
            execution_type=data["execution_type"],
            price=data.get("price") or stock.current_price,
            quantity=data["quantity"],
            trigger_price=data["trigger_price"],
        )
        logger.info(
            f"Conditional order created: {order.id} {order.execution_type} "
            f"{data['quantity']} {stock.symbol} @ trigger {data['trigger_price']}"
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

        # Conditional orders (stop_loss/take_profit) don't reserve cash/stock - nothing to refund
        is_conditional = order.execution_type in (
            Order.ExecutionType.STOP_LOSS,
            Order.ExecutionType.TAKE_PROFIT,
        )

        if remaining_qty > 0 and not is_conditional:
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
    current_price = float(stock.current_price)

    data = {
        "symbol": symbol,
        "bids": bids,
        "asks": asks,
        "bestBid": best_bid,
        "bestAsk": best_ask,
        "currentPrice": current_price,
        "spread": round(spread, 2),
        "spreadPercent": round(spread_pct, 4),
    }

    return Response(data)
