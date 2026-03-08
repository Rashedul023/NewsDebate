from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_token(request):
    """Test endpoint to verify JWT authentication"""
    return Response({
        'message': 'Authentication successful!',
        'user': {
            'id': request.user.id,
            'email': request.user.email,
            'full_name': request.user.full_name,
            'is_premium': request.user.is_premium,
        }
    })