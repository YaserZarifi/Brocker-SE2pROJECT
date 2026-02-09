import uuid

from django.conf import settings
from django.db import models


class Order(models.Model):
    """
    Represents a buy/sell order in the brokerage system.
    Maps to frontend Order interface.
    """

    class OrderType(models.TextChoices):
        BUY = "buy", "Buy"
        SELL = "sell", "Sell"

    class OrderStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        MATCHED = "matched", "Matched"
        PARTIAL = "partial", "Partially Filled"
        CANCELLED = "cancelled", "Cancelled"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    stock = models.ForeignKey(
        "stocks.Stock",
        on_delete=models.CASCADE,
        related_name="orders",
    )
    type = models.CharField(max_length=4, choices=OrderType.choices)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()
    filled_quantity = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"{self.get_type_display()} {self.quantity} {self.stock.symbol} @ {self.price}"

    @property
    def stock_symbol(self):
        return self.stock.symbol

    @property
    def stock_name(self):
        return self.stock.name

    @property
    def is_fully_filled(self):
        return self.filled_quantity >= self.quantity


class PortfolioHolding(models.Model):
    """
    Represents a user's holding in a specific stock.
    Maps to frontend PortfolioHolding interface.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="holdings",
    )
    stock = models.ForeignKey(
        "stocks.Stock",
        on_delete=models.CASCADE,
        related_name="holdings",
    )
    quantity = models.PositiveIntegerField(default=0)
    average_buy_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = ["user", "stock"]
        verbose_name = "Portfolio Holding"
        verbose_name_plural = "Portfolio Holdings"

    def __str__(self):
        return f"{self.user.username} - {self.stock.symbol} x{self.quantity}"

    @property
    def current_price(self):
        return self.stock.current_price

    @property
    def total_value(self):
        return self.quantity * self.stock.current_price

    @property
    def total_invested(self):
        return self.quantity * self.average_buy_price

    @property
    def profit_loss(self):
        return self.total_value - self.total_invested

    @property
    def profit_loss_percent(self):
        if self.total_invested > 0:
            return (self.profit_loss / self.total_invested) * 100
        return 0
