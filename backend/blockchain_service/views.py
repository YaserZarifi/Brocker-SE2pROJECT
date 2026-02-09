from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def blockchain_status(request):
    """
    Check the blockchain service status.
    Full implementation in Sprint 4.
    """
    return Response(
        {
            "status": "placeholder",
            "message": "Blockchain service will be implemented in Sprint 4.",
            "network": "hardhat-local",
        }
    )
