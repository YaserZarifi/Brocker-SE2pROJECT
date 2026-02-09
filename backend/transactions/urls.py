from django.urls import path

from . import views

app_name = "transactions"

urlpatterns = [
    path("", views.TransactionListView.as_view(), name="transaction_list"),
    path("<uuid:pk>/", views.TransactionDetailView.as_view(), name="transaction_detail"),
]
