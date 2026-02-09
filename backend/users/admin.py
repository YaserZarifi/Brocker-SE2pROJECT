from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "username", "role", "cash_balance", "is_active", "date_joined"]
    list_filter = ["role", "is_active", "is_staff"]
    search_fields = ["email", "username", "first_name", "last_name"]
    ordering = ["-date_joined"]

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Brokerage Info",
            {"fields": ("role", "wallet_address", "cash_balance")},
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Brokerage Info",
            {"fields": ("email", "role", "wallet_address")},
        ),
    )
