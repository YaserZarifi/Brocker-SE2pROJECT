from django.db import models


class Stock(models.Model):
    """
    Represents a listed stock in the brokerage system.
    Maps to frontend Stock interface.
    """

    symbol = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    name_fa = models.CharField(max_length=100, verbose_name="Name (Farsi)")
    current_price = models.DecimalField(max_digits=12, decimal_places=2)
    previous_close = models.DecimalField(max_digits=12, decimal_places=2)
    change = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    change_percent = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    volume = models.BigIntegerField(default=0)
    market_cap = models.BigIntegerField(default=0)
    high_24h = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    low_24h = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    open_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sector = models.CharField(max_length=50)
    sector_fa = models.CharField(max_length=50, verbose_name="Sector (Farsi)")
    logo = models.ImageField(upload_to="stock_logos/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["symbol"]
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"

    def __str__(self):
        return f"{self.symbol} - {self.name}"

    def update_price(self, new_price):
        """Update the stock price and recalculate derived fields."""
        self.previous_close = self.current_price
        self.current_price = new_price
        self.change = self.current_price - self.previous_close
        if self.previous_close > 0:
            self.change_percent = (self.change / self.previous_close) * 100
        self.save(update_fields=["current_price", "previous_close", "change", "change_percent", "updated_at"])


class PriceHistory(models.Model):
    """
    Historical price data for stocks (OHLCV).
    Maps to frontend PriceHistory interface.
    """

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="price_history")
    timestamp = models.DateField()
    open_price = models.DecimalField(max_digits=12, decimal_places=2)
    high = models.DecimalField(max_digits=12, decimal_places=2)
    low = models.DecimalField(max_digits=12, decimal_places=2)
    close = models.DecimalField(max_digits=12, decimal_places=2)
    volume = models.BigIntegerField(default=0)

    class Meta:
        ordering = ["-timestamp"]
        unique_together = ["stock", "timestamp"]
        verbose_name = "Price History"
        verbose_name_plural = "Price Histories"

    def __str__(self):
        return f"{self.stock.symbol} - {self.timestamp}"
