from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Article(models.Model):    
    # Core fields from NewsAPI
    title = models.CharField(max_length=500, db_index=True)
    content = models.TextField(blank=True, help_text="Description or content")
    image_url = models.URLField(max_length=500, blank=True)
    
    # Source information (simplified - just source name)
    source_name = models.CharField(max_length=200, db_index=True)
    
    # Publication info
    published_at = models.DateTimeField(db_index=True)
    url = models.URLField(max_length=500, unique=True)
    
    # Bias detection columns (for future ML model)
    bias_label = models.CharField(
        max_length=20,
        choices=[
            ('left', 'Left'),
            ('center', 'Center'),
            ('right', 'Right'),
            ('unclassified', 'Unclassified')
        ],
        default='unclassified',
        db_index=True
    )
    bias_score = models.FloatField(
        default=0.0,  # Default to 0 (neutral)
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)],
        help_text="Bias score from -1 (left) to +1 (right). Default 0 = neutral."
    )
    
    # Metadata
    fetched_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['bias_label', '-published_at']),
            models.Index(fields=['source_name', '-published_at']),
        ]
        # Prevent duplicate articles by title + source
        unique_together = ['title', 'source_name']
    
    def __str__(self):
        return self.title[:50]
    
    def save(self, *args, **kwargs):
        # Truncate content if too long for database
        if self.content and len(self.content) > 10000:
            self.content = self.content[:10000]
        # Truncate title if too long
        if self.title and len(self.title) > 500:
            self.title = self.title[:500]
        # Truncate source name if too long
        if self.source_name and len(self.source_name) > 200:
            self.source_name = self.source_name[:200]
        super().save(*args, **kwargs)