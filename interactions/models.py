from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator, MaxLengthValidator
from news.models import Article

class Upvote(models.Model):
    """User upvotes on articles"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='upvotes'
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='upvotes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'article']  # One upvote per user per article
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'article']),
            models.Index(fields=['article', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} ↑ {self.article.title[:30]}"


class Comment(models.Model):
    """User comments on articles"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    content = models.TextField(
        validators=[
            MinLengthValidator(1, message="Comment cannot be empty"),
            MaxLengthValidator(1000, message="Comment too long (max 1000 characters)")
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['article', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email}: {self.content[:30]}..."


class Ad(models.Model):
    """Advertisement for non-premium users"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, max_length=500)
    image_url = models.URLField(max_length=500, blank=True, 
                                 help_text="Leave blank for text-only ads")
    link_url = models.URLField(max_length=500)
    
    # Optional tracking
    click_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    
    # Scheduling
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text="Higher priority shows more often")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return self.title