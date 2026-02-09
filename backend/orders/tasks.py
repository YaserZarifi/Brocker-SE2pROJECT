"""
Celery tasks for the order matching system.
Sprint 3 - Async order processing via Celery + RabbitMQ

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
    Useful for catching any orders that might have been missed.
    """
    from .models import Order

    pending_orders = Order.objects.filter(
        status__in=[Order.OrderStatus.PENDING, Order.OrderStatus.PARTIAL]
    ).values_list("id", flat=True)

    count = 0
    for order_id in pending_orders:
        match_order_task.delay(str(order_id))
        count += 1

    logger.info(f"[Celery] Queued {count} pending orders for matching")
    return {"queued": count}
