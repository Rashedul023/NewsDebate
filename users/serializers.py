from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .utils import OTPService

class OTPRequestSerializer(serializers.Serializer):
    """Serializer for OTP request"""
    
    email = serializers.EmailField()
    purpose = serializers.ChoiceField(
        choices=['login', 'signup', 'reset'],
        default='login'
    )
    
    def validate_email(self, value):
        """Basic email validation"""
        if not value:
            raise serializers.ValidationError("Email is required")
        return value.lower()

class OTPVerifySerializer(serializers.Serializer):
    """Serializer for OTP verification"""
    
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6, min_length=6)
    purpose = serializers.ChoiceField(
        choices=['login', 'signup', 'reset'],
        default='login'
    )
    
    def validate_code(self, value):
        """Validate code is digits"""
        if not value.isdigit():
            raise serializers.ValidationError("Code must contain only digits")
        return value

class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'is_premium', 
            'is_premium_active', 'email_verified', 'date_joined'
        ]
        read_only_fields = ['id', 'is_premium', 'date_joined']

class TokenResponseSerializer(serializers.Serializer):
    """Serializer for token response"""
    
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()

    def to_representation(self, instance):
        """Custom representation"""
        user, tokens = instance
        return {
            'access': str(tokens['access']),
            'refresh': str(tokens['refresh']),
            'user': UserSerializer(user).data
        }

class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating profile"""
    
    class Meta:
        model = User
        fields = ['full_name', 'receive_notifications']
    
    def update(self, instance, validated_data):
        """Update user profile"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class UserActivitySerializer(serializers.Serializer):
    """Serializer for user activity"""
    
    total_votes = serializers.IntegerField()
    total_comments = serializers.IntegerField()
    member_since = serializers.DateTimeField()
    last_active = serializers.DateTimeField()