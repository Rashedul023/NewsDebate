# news/serializers.py
from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    """
    Full article serializer - converts Article model to JSON
    Includes all fields plus computed properties
    """
    # Computed fields (not in database, calculated on the fly)
    days_since_published = serializers.SerializerMethodField()
    bias_display = serializers.CharField(source='get_bias_label_display', read_only=True)
    summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id',
            'title',
            'content',
            'summary',
            'image_url',
            'source_name',
            'published_at',
            'url',
            'bias_label',
            'bias_display',
            'bias_score',
            'days_since_published',
            'is_active',
            'fetched_at',
        ]
        read_only_fields = fields  # All fields are read-only (no create/update)
    
    def get_days_since_published(self, obj):
        """Calculate how many days ago this article was published"""
        from django.utils import timezone
        delta = timezone.now() - obj.published_at
        return delta.days
    
    def get_summary(self, obj):
        """Return first 150 characters as summary"""
        if obj.content:
            return obj.content[:150] + '...' if len(obj.content) > 150 else obj.content
        return "No content available"

class ArticleListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views (faster responses)
    Used when showing multiple articles
    """
    bias_display = serializers.CharField(source='get_bias_label_display', read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'id',
            'title',
            'source_name',
            'published_at',
            'image_url',
            'bias_label',
            'bias_display',
            'bias_score',
        ]