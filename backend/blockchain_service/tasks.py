"""
Celery tasks for blockchain transaction recording.
Sprint 4 - Blockchain Integration

After the matching engine creates a Transaction, a Celery task is fired
(via ``transaction.on_commit``) to record the trade on the private Hardhat
blockchain.  In dev mode (``CELERY_TASK_ALWAYS_EAGER=True``), the task
executes synchronously inside the same request.
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    name="blockchain.record_transaction",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    acks_late=True,
)
def record_transaction_on_blockchain(self, transaction_id):
    """
    Record a matched transaction on the blockchain and update
    ``Transaction.blockchain_hash``.

    Args:
        transaction_id: UUID string of the Transaction to record.

    Returns:
        dict with result info.
    """
    from transactions.models import Transaction

    from .service import get_blockchain_service

    try:
        tx = Transaction.objects.select_related("stock", "buyer", "seller").get(
            id=transaction_id
        )

        if tx.blockchain_hash:
            logger.info("TX %s already has blockchain hash – skipping", transaction_id)
            return {
                "transaction_id": str(transaction_id),
                "status": "already_recorded",
                "blockchain_hash": tx.blockchain_hash,
            }

        service = get_blockchain_service()
        tx_hash = service.record_transaction(tx)

        if tx_hash:
            tx.blockchain_hash = tx_hash
            tx.save(update_fields=["blockchain_hash"])
            logger.info(
                "TX %s blockchain_hash updated: %s", transaction_id, tx_hash
            )
            return {
                "transaction_id": str(transaction_id),
                "status": "recorded",
                "blockchain_hash": tx_hash,
            }

        logger.warning(
            "Blockchain recording returned None for TX %s (node down?)",
            transaction_id,
        )
        return {
            "transaction_id": str(transaction_id),
            "status": "skipped",
            "blockchain_hash": None,
        }

    except Transaction.DoesNotExist:
        logger.error("Transaction %s not found in DB", transaction_id)
        return {"transaction_id": str(transaction_id), "status": "not_found"}

    except Exception as exc:
        logger.error(
            "Error in blockchain recording for TX %s: %s",
            transaction_id,
            exc,
            exc_info=True,
        )
        raise self.retry(exc=exc)
