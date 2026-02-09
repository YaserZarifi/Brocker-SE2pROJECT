from django.contrib import admin

from .models import PriceHistory, Stock


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ["symbol", "name", "name_fa", "current_price", "change", "change_percent", "volume", "sector", "is_active"]
    list_filter = ["sector", "is_active"]
    search_fields = ["symbol", "name", "name_fa"]
    ordering = ["symbol"]


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ["stock", "timestamp", "open_price", "high", "low", "close", "volume"]
    list_filter = ["stock", "timestamp"]
    ordering = ["-timestamp"]
