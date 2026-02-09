"""
Blockchain Service API Views
Sprint 4 - Blockchain Integration

Endpoints:
  GET  /api/v1/blockchain/status/              – Blockchain connection status
  GET  /api/v1/blockchain/verify/<uuid:tx_id>/ – Verify a transaction on-chain
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .service import get_blockchain_service


@api_view(["GET"])
@permission_classes([AllowAny])
def blockchain_status(request):
    """
    Return the current status of the blockchain service.

    Includes connection info, chain ID, block number, contract address,
    and on-chain trade count.
    """
    service = get_blockchain_service()
    return Response(service.get_status())


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def verify_transaction(request, tx_id):
    """
    Verify that a transaction is recorded on the blockchain.

    Returns on-chain data (stock symbol, price, quantity, total value,
    timestamp) if the record exists, or a not-found indicator otherwise.
    """
    service = get_blockchain_service()
    result = service.verify_transaction(str(tx_id))
    return Response(result)
