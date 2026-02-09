from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    """List all notifications for the authenticated user."""

    serializer_class = NotificationSerializer
    filterset_fields = ["type", "read"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationDetailView(generics.RetrieveUpdateAPIView):
    """Get or update (mark as read) a notification."""

    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(read=True)


@api_view(["POST"])
def mark_all_read(request):
    """Mark all notifications as read for the authenticated user."""
    count = Notification.objects.filter(user=request.user, read=False).update(read=True)
    return Response({"message": f"{count} notifications marked as read."})


@api_view(["GET"])
def unread_count(request):
    """Get the count of unread notifications."""
    count = Notification.objects.filter(user=request.user, read=False).count()
    return Response({"unreadCount": count})
