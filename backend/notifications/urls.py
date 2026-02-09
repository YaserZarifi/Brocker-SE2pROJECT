from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.NotificationListView.as_view(), name="notification_list"),
    path("mark-all-read/", views.mark_all_read, name="mark_all_read"),
    path("unread-count/", views.unread_count, name="unread_count"),
    path("<uuid:pk>/", views.NotificationDetailView.as_view(), name="notification_detail"),
]
