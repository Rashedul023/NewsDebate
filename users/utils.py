import logging
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from .models import OTP, User

logger = logging.getLogger(__name__)

class OTPRateLimiter:
    """Rate limiting for OTP requests"""
    
    def __init__(self, email, purpose='login'):
        self.email = email
        self.purpose = purpose
        self.cache_key = f"otp_rate_{email}_{purpose}"
    
    def can_request(self):
        """Check if user can request new OTP"""
        attempts = cache.get(self.cache_key, 0)
        
        if attempts >= 3:
            return False, "Too many OTP requests. Please try after 15 minutes."
        
        return True, "OK"
    
    def increment(self):
        """Increment request counter"""
        attempts = cache.get(self.cache_key, 0)
        cache.set(self.cache_key, attempts + 1, timeout=900)  # 15 minutes
    
    def reset(self):
        """Reset rate limit after successful verification"""
        cache.delete(self.cache_key)

class OTPService:
    """Service for OTP operations"""
    
    @staticmethod
    def request_otp(email, purpose='login'):
        """Request a new OTP"""
        
        # Rate limiting
        limiter = OTPRateLimiter(email, purpose)
        allowed, message = limiter.can_request()
        
        if not allowed:
            return {'success': False, 'message': message}
        
        try:
            # Get or create user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'full_name': email.split('@')[0]}
            )
            
            # Create OTP
            otp = OTP.create_for_user(user, purpose)
            
            limiter.increment()
            
            logger.info(f"OTP generated for {email}: {otp.code}")
            
            # In development, log the code for testing
            if not created:
                print(f"\n🔐 DEVELOPMENT: OTP for {email} is: {otp.code}\n")
            
            return {
                'success': True,
                'message': 'OTP sent successfully',
                'user_exists': not created,
                'otp': otp.code if not created else None,  # Only in dev!
            }
            
        except Exception as e:
            logger.error(f"OTP request failed for {email}: {e}")
            return {'success': False, 'message': 'Failed to send OTP'}
    
    @staticmethod
    def verify_otp(email, code, purpose='login'):
        """Verify OTP code"""
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return {'success': False, 'message': 'User not found'}
        
        # Get latest OTP
        otp = OTP.objects.filter(
            user=user,
            purpose=purpose,
            is_used=False
        ).first()
        
        if not otp:
            return {'success': False, 'message': 'No active OTP found'}
        
        # Verify
        success, message = otp.verify(code)
        
        if success:
            # Reset rate limiter
            limiter = OTPRateLimiter(email, purpose)
            limiter.reset()
            
            # Mark email as verified
            user.email_verified = True
            user.save(update_fields=['email_verified'])
            
            return {
                'success': True,
                'message': 'OTP verified',
                'user': user
            }
        
        return {'success': False, 'message': message}