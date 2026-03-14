from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

urlpatterns = [
    # JWT endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Protected test endpoint
    path('test/', views.test_token, name='test_token'),

    # User endpoints
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),

    # OTP endpoints
    path('request-otp/', views.request_otp, name='request_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),

    # Additional endpoints
    path('activity/', views.activity, name='activity'),
    path('preferences/', views.change_preferences, name='preferences'),
    path('delete-account/', views.delete_account, name='delete_account'),
]