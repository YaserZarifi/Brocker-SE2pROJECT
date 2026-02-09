from django.contrib import admin

from .models import Order, PortfolioHolding


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "stock", "type", "price", "quantity", "filled_quantity", "status", "created_at"]
    list_filter = ["type", "status", "created_at"]
    search_fields = ["user__email", "stock__symbol"]
    ordering = ["-created_at"]
    raw_id_fields = ["user", "stock"]


@admin.register(PortfolioHolding)
class PortfolioHoldingAdmin(admin.ModelAdmin):
    list_display = ["user", "stock", "quantity", "average_buy_price"]
    list_filter = ["stock"]
    search_fields = ["user__email", "stock__symbol"]
    raw_id_fields = ["user", "stock"]
