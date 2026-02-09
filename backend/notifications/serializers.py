from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model - maps to frontend Notification interface."""

    userId = serializers.UUIDField(source="user_id", read_only=True)
    titleFa = serializers.CharField(source="title_fa", read_only=True)
    messageFa = serializers.CharField(source="message_fa", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "userId",
            "title",
            "titleFa",
            "message",
            "messageFa",
            "type",
            "read",
            "createdAt",
        ]
        read_only_fields = ["id", "userId", "createdAt"]
