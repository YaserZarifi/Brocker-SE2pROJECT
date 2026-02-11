"""
Celery tasks for the order matching system.
Sprint 3 - Async order processing via Celery + RabbitMQ
Sprint 4 - Blockchain recording is triggered via on_commit in matching.py

In development (CELERY_TASK_ALWAYS_EAGER=True), tasks run synchronously.
In production, tasks are sent to RabbitMQ and processed by Celery workers.
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    name="orders.match_order",
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    acks_late=True,
)
def match_order_task(self, order_id):
    """
    Celery task to match an order asynchronously.

    Args:
        order_id: UUID string of the order to match

    Returns:
        dict with match results
    """
    from .matching import match_order

    try:
        logger.info(f"[Celery] Starting matching for order {order_id}")
        transactions = match_order(order_id)
        result = {
            "order_id": str(order_id),
            "transactions_created": len(transactions),
            "transaction_ids": [str(tx.id) for tx in transactions],
        }
        logger.info(
            f"[Celery] Order {order_id}: {len(transactions)} transaction(s) created"
        )
        return result
    except Exception as exc:
        logger.error(f"[Celery] Error matching order {order_id}: {exc}", exc_info=True)
        raise self.retry(exc=exc)


@shared_task(name="orders.match_all_pending")
def match_all_pending_task():
    """
    Periodic task to attempt matching all pending/partial orders.
    Excludes Stop-Loss/Take-Profit (handled by check_conditional_orders_task).
    """
    from .models import Order

    pending_orders = Order.objects.filter(
        status__in=[Order.OrderStatus.PENDING, Order.OrderStatus.PARTIAL],
        execution_type__in=[Order.ExecutionType.LIMIT, Order.ExecutionType.MARKET],
    ).values_list("id", flat=True)

    count = 0
    for order_id in pending_orders:
        match_order_task.delay(str(order_id))
        count += 1

    logger.info(f"[Celery] Queued {count} pending orders for matching")
    return {"queued": count}


@shared_task(name="orders.check_conditional_orders")
def check_conditional_orders_task():
    """
    Check Stop-Loss and Take-Profit orders; convert triggered ones to market and match.
    Run periodically via Celery Beat (e.g. every 30 seconds).
    """
    from django.db import transaction as db_transaction

    from .matching import match_order
    from .models import Order, PortfolioHolding

    from .views import _get_order_book_prices

    triggered = 0
    for order in Order.objects.filter(
        status__in=[Order.OrderStatus.PENDING, Order.OrderStatus.PARTIAL],
        execution_type__in=[
            Order.ExecutionType.STOP_LOSS,
            Order.ExecutionType.TAKE_PROFIT,
        ],
    ).select_related("stock", "user"):
        stock = order.stock
        trigger = order.trigger_price
        current = stock.current_price

        should_trigger = False
        if order.execution_type == Order.ExecutionType.STOP_LOSS:
            if order.type == Order.OrderType.SELL and current <= trigger:
                should_trigger = True
            elif order.type == Order.OrderType.BUY and current >= trigger:
                should_trigger = True
        elif order.execution_type == Order.ExecutionType.TAKE_PROFIT:
            if order.type == Order.OrderType.SELL and current >= trigger:
                should_trigger = True
            elif order.type == Order.OrderType.BUY and current <= trigger:
                should_trigger = True

        if not should_trigger:
            continue

        try:
            with db_transaction.atomic():
                if order.type == Order.OrderType.SELL:
                    holding = PortfolioHolding.objects.select_for_update().filter(
                        user=order.user, stock=stock
                    ).first()
                    if not holding or holding.quantity < order.quantity:
                        order.status = Order.OrderStatus.CANCELLED
                        order.save(update_fields=["status", "updated_at"])
                        logger.warning(
                            f"Conditional sell {order.id} cancelled: insufficient holdings"
                        )
                        continue
                    holding.quantity -= order.quantity
                    holding.save(update_fields=["quantity"])
                    best_ask, best_bid = _get_order_book_prices(stock)
                    order.price = best_bid if best_bid else stock.current_price
                else:
                    best_ask, _ = _get_order_book_prices(stock)
                    price = best_ask if best_ask else stock.current_price
                    if price <= 0:
                        continue
                    total = price * order.quantity
                    user = type(order.user).objects.select_for_update().get(
                        pk=order.user.pk
                    )
                    if user.cash_balance < total:
                        order.status = Order.OrderStatus.CANCELLED
                        order.save(update_fields=["status", "updated_at"])
                        logger.warning(
                            f"Conditional buy {order.id} cancelled: insufficient cash"
                        )
                        continue
                    user.cash_balance -= total
                    user.save(update_fields=["cash_balance"])
                    order.price = price

                order.execution_type = Order.ExecutionType.MARKET
                order.save(update_fields=["execution_type", "price", "updated_at"])
                triggered += 1
                match_order(str(order.id))
        except Exception as exc:
            logger.exception(f"Failed to trigger conditional order {order.id}: {exc}")

    if triggered:
        logger.info(f"[Celery] Triggered {triggered} conditional orders")
    return {"triggered": triggered}
