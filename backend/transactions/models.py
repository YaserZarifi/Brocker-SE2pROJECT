import uuid

from django.conf import settings
from django.db import models


class Transaction(models.Model):
    """
    Represents an executed trade (matched buy + sell orders).
    Maps to frontend Transaction interface.
    """

    class TransactionStatus(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmed"
        PENDING = "pending", "Pending"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buy_order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="buy_transactions",
    )
    sell_order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="sell_transactions",
    )
    stock = models.ForeignKey(
        "stocks.Stock",
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()
    total_value = models.DecimalField(max_digits=15, decimal_places=2)
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="purchases",
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sales",
    )
    blockchain_hash = models.CharField(max_length=66, blank=True, null=True)
    executed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING,
    )

    class Meta:
        ordering = ["-executed_at"]
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"TX {self.id} - {self.quantity} {self.stock.symbol} @ {self.price}"

    def save(self, *args, **kwargs):
        if not self.total_value:
            self.total_value = self.price * self.quantity
        super().save(*args, **kwargs)
