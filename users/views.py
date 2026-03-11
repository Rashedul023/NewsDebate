from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
import logging

from .models import User
from .serializers import (
    OTPRequestSerializer, OTPVerifySerializer,
    UserSerializer, TokenResponseSerializer
)
from .utils import OTPService

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def request_otp(request):
    """
    Request OTP for login/signup
    
    POST /api/auth/request-otp/
    {
        "email": "user@example.com",
        "purpose": "login"  # or "signup", "reset"
    }
    """
    serializer = OTPRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    purpose = serializer.validated_data['purpose']
    
    result = OTPService.request_otp(email, purpose)
    
    if result['success']:
        return Response({
            'message': result['message'],
            'email': email,
            'purpose': purpose,
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': result['message']
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """
    Verify OTP and return JWT tokens
    
    POST /api/auth/verify-otp/
    {
        "email": "user@example.com",
        "code": "123456",
        "purpose": "login"
    }
    """
    serializer = OTPVerifySerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    code = serializer.validated_data['code']
    purpose = serializer.validated_data['purpose']
    
    # Verify OTP
    result = OTPService.verify_otp(email, code, purpose)
    
    if not result['success']:
        return Response({
            'error': result['message']
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = result['user']
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    tokens = {
        'access': refresh.access_token,
        'refresh': refresh,
    }
    
    # Log login
    logger.info(f"User logged in: {user.email}")
    
    # Return tokens and user data
    response_data = {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'is_premium': user.is_premium,
            'is_premium_active': user.is_premium_active,
            'email_verified': user.email_verified,
        }
    }
    
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout user by blacklisting refresh token
    
    POST /api/auth/logout/
    {
        "refresh": "refresh-token-here"
    }
    """
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logged out successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile(request):
    """
    Get or update user profile
    
    GET  /api/auth/profile/ - Get profile
    PUT/PATCH /api/auth/profile/ - Update profile
    """
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    # Update profile
    data = request.data.copy()
    # Don't allow email change via this endpoint
    data.pop('email', None)
    
    serializer = UserSerializer(request.user, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            'is_premium_active': request.user.is_premium_active,
        }
    })