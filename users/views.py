from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import logging

from .models import User
from .serializers import (
    OTPRequestSerializer, OTPVerifySerializer,
    UserSerializer
)
from .utils import OTPService

logger = logging.getLogger(__name__)


# ========== OTP Authentication Views ==========

@csrf_exempt
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
    # Debug prints (remove in production)
    print(f"Request method: {request.method}")
    print(f"Request headers: {dict(request.headers)}")
    print(f"CSRF token in request: {request.META.get('CSRF_COOKIE')}")
    
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


@csrf_exempt
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


# ========== JWT Token Management ==========

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
        if not refresh_token:
            return Response(
                {'error': 'Refresh token required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logged out successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ========== User Profile Views ==========

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


# ========== User Activity & Preferences ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity(request):
    """
    Get user activity summary
    
    GET /api/auth/activity/
    """
    # Placeholder until voting and comments are fully implemented
    return Response({
        'total_upvotes': 0,  # Will be replaced with actual count
        'total_comments': 0,  # Will be replaced with actual count
        'member_since': request.user.date_joined,
        'last_active': request.user.last_login or request.user.date_joined,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_preferences(request):
    """
    Change user preferences
    
    POST /api/auth/preferences/
    {
        "receive_notifications": true
    }
    """
    user = request.user
    notifications = request.data.get('receive_notifications', user.receive_notifications)
    
    user.receive_notifications = notifications
    user.save(update_fields=['receive_notifications'])
    
    return Response({
        'message': 'Preferences updated',
        'receive_notifications': user.receive_notifications
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """
    Delete (deactivate) user account
    
    DELETE /api/auth/delete-account/
    """
    user = request.user
    user.is_active = False
    user.save(update_fields=['is_active'])
    
    # Optional: Blacklist current refresh token
    try:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            # Token blacklisting would go here
            pass
    except:
        pass
    
    return Response({
        'message': 'Account deactivated successfully'
    })


# ========== Test Endpoints ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_token(request):
    """
    Test endpoint to verify JWT authentication
    
    GET /api/auth/test/
    """
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


# ========== Frontend Page Views ==========

def login_page(request):
    """Render login page"""
    return render(request, 'users/login.html')