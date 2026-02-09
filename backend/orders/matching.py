"""
BourseChain Matching Engine
Sprint 3 - Price-Time Priority Matching Algorithm

The matching engine follows a price-time priority algorithm:
- For BUY orders: matches against the cheapest available SELL orders first
- For SELL orders: matches against the highest available BUY orders first
- At the same price level, orders that arrived first get matched first (FIFO)

Cash/Stock flow:
- Buy order creation: cash is reserved (deducted from balance)
- Sell order creation: stock is reserved (deducted from holdings)
- Match: buyer gets stock, seller gets cash
- Cancel: unfilled portion is refunded
"""

import logging
from decimal import Decimal

from django.db import transaction as db_transaction

from notifications.models import Notification
from transactions.models import Transaction

from .models import Order, PortfolioHolding

logger = logging.getLogger(__name__)


def match_order(order_id):
    """
    Try to match an order against existing orders in the book.

    Args:
        order_id: UUID of the order to match

    Returns:
        list: List of created Transaction objects
    """
    try:
        order = Order.objects.select_related("stock", "user").get(
            id=order_id,
            status__in=[Order.OrderStatus.PENDING, Order.OrderStatus.PARTIAL],
        )
    except Order.DoesNotExist:
        logger.warning(f"Order {order_id} not found or not matchable")
        return []

    if order.type == Order.OrderType.BUY:
        return _match_buy_order(order)
    else:
        return _match_sell_order(order)


def _match_buy_order(buy_order):
    """
    Match a buy order against existing sell orders.
    Find sell orders where sell_price <= buy_price, sorted by:
    1. Price ASC (cheapest sell first)
    2. Created time ASC (oldest first - FIFO)
    """
    matching_sells = (
        Order.objects.filter(
            stock=buy_order.stock,
            type=Order.OrderType.SELL,
            status__in=[Order.OrderStatus.PENDING, Order.OrderStatus.PARTIAL],
            price__lte=buy_order.price,
        )
        .exclude(user=buy_order.user)  # Can't trade with yourself
        .select_related("stock", "user")
        .order_by("price", "created_at")
    )

    transactions = []

    for sell_order in matching_sells:
        if buy_order.filled_quantity >= buy_order.quantity:
            break  # Buy order fully filled

        tx = _execute_match(buy_order, sell_order)
        if tx:
            transactions.append(tx)

    return transactions


def _match_sell_order(sell_order):
    """
    Match a sell order against existing buy orders.
    Find buy orders where buy_price >= sell_price, sorted by:
    1. Price DESC (highest buy first)
    2. Created time ASC (oldest first - FIFO)
    """
    matching_buys = (
        Order.objects.filter(
            stock=sell_order.stock,
            type=Order.OrderType.BUY,
            status__in=[Order.OrderStatus.PENDING, Order.OrderStatus.PARTIAL],
            price__gte=sell_order.price,
        )
        .exclude(user=sell_order.user)  # Can't trade with yourself
        .select_related("stock", "user")
        .order_by("-price", "created_at")
    )

    transactions = []

    for buy_order in matching_buys:
        if sell_order.filled_quantity >= sell_order.quantity:
            break  # Sell order fully filled

        tx = _execute_match(buy_order, sell_order)
        if tx:
            transactions.append(tx)

    return transactions


@db_transaction.atomic
def _execute_match(buy_order, sell_order):
    """
    Execute a match between a buy order and a sell order.
    Uses database-level atomic transaction to ensure consistency.

    Execution price = maker's price (the order that was already in the book).
    """
    # Refresh from DB to get latest filled_quantity (prevent race conditions)
    buy_order.refresh_from_db()
    sell_order.refresh_from_db()

    buy_remaining = buy_order.quantity - buy_order.filled_quantity
    sell_remaining = sell_order.quantity - sell_order.filled_quantity

    if buy_remaining <= 0 or sell_remaining <= 0:
        return None

    # Matched quantity is the minimum of remaining quantities
    matched_qty = min(buy_remaining, sell_remaining)

    # Execution price: maker's price (the older order that was in the book first)
    if buy_order.created_at <= sell_order.created_at:
        execution_price = buy_order.price
    else:
        execution_price = sell_order.price

    total_value = execution_price * matched_qty

    logger.info(
        f"Matching: {matched_qty} {buy_order.stock.symbol} @ {execution_price} "
        f"(Buy #{buy_order.id} <-> Sell #{sell_order.id})"
    )

    # --- 1. Create Transaction ---
    tx = Transaction.objects.create(
        buy_order=buy_order,
        sell_order=sell_order,
        stock=buy_order.stock,
        price=execution_price,
        quantity=matched_qty,
        total_value=total_value,
        buyer=buy_order.user,
        seller=sell_order.user,
        status=Transaction.TransactionStatus.CONFIRMED,
    )

    # --- 2. Update Order filled quantities and statuses ---
    buy_order.filled_quantity += matched_qty
    sell_order.filled_quantity += matched_qty

    _update_order_status(buy_order)
    _update_order_status(sell_order)

    buy_order.save(update_fields=["filled_quantity", "status", "updated_at"])
    sell_order.save(update_fields=["filled_quantity", "status", "updated_at"])

    # --- 3. Update cash balances ---
    # Buy side: Cash was reserved at buy_order.price on creation.
    # If execution_price < buy_order.price, refund the price difference.
    if execution_price < buy_order.price:
        price_diff = buy_order.price - execution_price
        refund = price_diff * matched_qty
        buy_order.user.cash_balance += refund
        buy_order.user.save(update_fields=["cash_balance"])

    # Sell side: Seller receives cash at execution price
    sell_order.user.cash_balance += total_value
    sell_order.user.save(update_fields=["cash_balance"])

    # --- 4. Update Portfolio Holdings ---
    # Buyer gets stock
    buyer_holding, _ = PortfolioHolding.objects.get_or_create(
        user=buy_order.user,
        stock=buy_order.stock,
        defaults={"quantity": 0, "average_buy_price": Decimal("0")},
    )
    # Update weighted average buy price
    old_total_cost = buyer_holding.quantity * buyer_holding.average_buy_price
    new_cost = matched_qty * execution_price
    new_quantity = buyer_holding.quantity + matched_qty
    if new_quantity > 0:
        buyer_holding.average_buy_price = (old_total_cost + new_cost) / new_quantity
    buyer_holding.quantity = new_quantity
    buyer_holding.save(update_fields=["quantity", "average_buy_price"])

    # Seller's stock was already deducted from holdings on order creation

    # --- 5. Update Stock Price & Volume ---
    stock = buy_order.stock
    stock.previous_close = stock.current_price
    stock.current_price = execution_price
    stock.change = stock.current_price - stock.previous_close
    if stock.previous_close > 0:
        stock.change_percent = (stock.change / stock.previous_close) * 100
    stock.volume += matched_qty
    if execution_price > stock.high_24h:
        stock.high_24h = execution_price
    if stock.low_24h == 0 or execution_price < stock.low_24h:
        stock.low_24h = execution_price
    stock.save(
        update_fields=[
            "current_price",
            "previous_close",
            "change",
            "change_percent",
            "volume",
            "high_24h",
            "low_24h",
            "updated_at",
        ]
    )

    # --- 6. Send Notifications ---
    _send_match_notifications(
        buy_order, sell_order, matched_qty, execution_price, total_value
    )

    return tx


def _update_order_status(order):
    """Update order status based on filled quantity."""
    if order.filled_quantity >= order.quantity:
        order.status = Order.OrderStatus.MATCHED
    elif order.filled_quantity > 0:
        order.status = Order.OrderStatus.PARTIAL


def _send_match_notifications(buy_order, sell_order, quantity, price, total_value):
    """Send bilingual notifications to both buyer and seller."""
    stock_symbol = buy_order.stock.symbol
    stock_name = buy_order.stock.name
    stock_name_fa = buy_order.stock.name_fa

    price_fmt = f"{price:,.0f}"
    total_fmt = f"{total_value:,.0f}"

    # Notification for buyer
    Notification.objects.create(
        user=buy_order.user,
        title=f"Order Matched: Bought {quantity} {stock_symbol}",
        title_fa=f"سفارش تطبیق شد: خرید {quantity} سهم {stock_name_fa}",
        message=(
            f"Your buy order for {quantity} shares of {stock_name} ({stock_symbol}) "
            f"was matched at {price_fmt} IRR per share. Total: {total_fmt} IRR."
        ),
        message_fa=(
            f"سفارش خرید شما برای {quantity} سهم {stock_name_fa} ({stock_symbol}) "
            f"با قیمت {price_fmt} ریال به ازای هر سهم تطبیق شد. مجموع: {total_fmt} ریال."
        ),
        type=Notification.NotificationType.ORDER_MATCHED,
    )

    # Notification for seller
    Notification.objects.create(
        user=sell_order.user,
        title=f"Order Matched: Sold {quantity} {stock_symbol}",
        title_fa=f"سفارش تطبیق شد: فروش {quantity} سهم {stock_name_fa}",
        message=(
            f"Your sell order for {quantity} shares of {stock_name} ({stock_symbol}) "
            f"was matched at {price_fmt} IRR per share. Total: {total_fmt} IRR."
        ),
        message_fa=(
            f"سفارش فروش شما برای {quantity} سهم {stock_name_fa} ({stock_symbol}) "
            f"با قیمت {price_fmt} ریال به ازای هر سهم تطبیق شد. مجموع: {total_fmt} ریال."
        ),
        type=Notification.NotificationType.ORDER_MATCHED,
    )
