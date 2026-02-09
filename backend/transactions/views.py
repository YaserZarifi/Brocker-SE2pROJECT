from django.db.models import Q
from rest_framework import generics

from .models import Transaction
from .serializers import TransactionSerializer


class TransactionListView(generics.ListAPIView):
    """List all transactions for the authenticated user (as buyer or seller)."""

    serializer_class = TransactionSerializer
    filterset_fields = ["status"]
    ordering_fields = ["executed_at", "price", "quantity", "total_value"]

    def get_queryset(self):
        return (
            Transaction.objects.filter(Q(buyer=self.request.user) | Q(seller=self.request.user))
            .select_related("stock", "buy_order", "sell_order")
        )


class TransactionDetailView(generics.RetrieveAPIView):
    """Get a single transaction."""

    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(
            Q(buyer=self.request.user) | Q(seller=self.request.user)
        ).select_related("stock", "buy_order", "sell_order")
