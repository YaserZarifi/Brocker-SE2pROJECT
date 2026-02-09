from django.urls import path

from . import views

app_name = "blockchain_service"

urlpatterns = [
    path("status/", views.blockchain_status, name="blockchain_status"),
]
