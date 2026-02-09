from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "title", "type", "read", "created_at"]
    list_filter = ["type", "read", "created_at"]
    search_fields = ["user__email", "title", "message"]
    ordering = ["-created_at"]
    raw_id_fields = ["user"]
