from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["id", "stock", "price", "quantity", "total_value", "buyer", "seller", "status", "executed_at"]
    list_filter = ["status", "executed_at"]
    search_fields = ["stock__symbol", "buyer__email", "seller__email", "blockchain_hash"]
    ordering = ["-executed_at"]
    raw_id_fields = ["buy_order", "sell_order", "buyer", "seller", "stock"]
