from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from datetime import timedelta

class CustomUserManager(BaseUserManager):
    """Custom manager for User model with email as username"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError('Email is required')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model with email as username"""
    
    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': 'A user with this email already exists.'
        }
    )
    
    # Personal info
    full_name = models.CharField(max_length=255, blank=True)
    
    # Premium status
    is_premium = models.BooleanField(default=False)
    premium_until = models.DateTimeField(null=True, blank=True)
    
    # Status flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Email verification
    email_verified = models.BooleanField(default=False)
    
    # Settings
    receive_notifications = models.BooleanField(default=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # No additional required fields
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_premium']),
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return full name"""
        return self.full_name or self.email
    
    def get_short_name(self):
        """Return short name (first part of email)"""
        return self.email.split('@')[0]
    
    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send email to this user"""
        send_mail(subject, message, from_email, [self.email], **kwargs)
    
    @property
    def is_premium_active(self):
        """Check if premium subscription is active"""
        if not self.is_premium:
            return False
        if not self.premium_until:
            return True  # Lifetime premium
        return self.premium_until > timezone.now()
    


class OTP(models.Model):
    """One-Time Password for email verification"""
    
    PURPOSE_CHOICES = [
        ('login', 'Login'),
        ('signup', 'Sign Up'),
        ('reset', 'Password Reset'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='otps'
    )
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES, default='login')
    
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    # Track attempts for rate limiting
    attempts = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'purpose', 'is_used']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.code} - {'Used' if self.is_used else 'Active'}"
    
    def save(self, *args, **kwargs):
        """Set expiry if not provided"""
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)  # 10 minutes expiry
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if OTP is valid (not used, not expired)"""
        return not self.is_used and not self.is_expired
    
    @classmethod
    def generate_code(cls):
        """Generate a 6-digit OTP code"""
        return ''.join(random.choices(string.digits, k=6))
    
    @classmethod
    def create_for_user(cls, user, purpose='login'):
        """Create a new OTP for user, invalidating previous ones"""
        # Mark previous OTPs as used
        cls.objects.filter(
            user=user, 
            purpose=purpose, 
            is_used=False
        ).update(is_used=True)
        
        # Create new OTP
        return cls.objects.create(
            user=user,
            code=cls.generate_code(),
            purpose=purpose
        )
    
    def verify(self, code):
        """Verify OTP code"""
        self.attempts += 1
        self.save(update_fields=['attempts'])
        
        if self.attempts > 5:
            return False, "Too many attempts. Please request new OTP."
        
        if self.is_used:
            return False, "OTP already used"
        
        if self.is_expired:
            return False, "OTP expired"
        
        if self.code != code:
            return False, "Invalid code"
        
        # Mark as used on success
        self.is_used = True
        self.save(update_fields=['is_used'])
        
        return True, "OTP verified successfully"