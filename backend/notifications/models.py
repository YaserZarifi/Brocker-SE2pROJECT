import uuid

from django.conf import settings
from django.db import models


class Notification(models.Model):
    """
    Represents a notification sent to a user.
    Maps to frontend Notification interface.
    """

    class NotificationType(models.TextChoices):
        ORDER_MATCHED = "order_matched", "Order Matched"
        ORDER_CANCELLED = "order_cancelled", "Order Cancelled"
        PRICE_ALERT = "price_alert", "Price Alert"
        SYSTEM = "system", "System"
        TRANSACTION = "transaction", "Transaction"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=200)
    title_fa = models.CharField(max_length=200, verbose_name="Title (Farsi)")
    message = models.TextField()
    message_fa = models.TextField(verbose_name="Message (Farsi)")
    type = models.CharField(max_length=20, choices=NotificationType.choices)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.title} - {self.user.username}"
