import django_filters
from django.db import models
from .models import Article

class ArticleFilter(django_filters.FilterSet):
    """
    Advanced filtering for articles
    Allows queries like:
    - /api/articles/?from_date=2024-01-01
    - /api/articles/?bias=left&source=CNN
    - /api/articles/?search=election
    """
    
    # Date filters
    from_date = django_filters.DateTimeFilter(
        field_name='published_at', 
        lookup_expr='gte',
        help_text="Articles published after this date (YYYY-MM-DD)"
    )
    to_date = django_filters.DateTimeFilter(
        field_name='published_at', 
        lookup_expr='lte',
        help_text="Articles published before this date (YYYY-MM-DD)"
    )
    
    # Source filter
    source = django_filters.CharFilter(
        field_name='source_name', 
        lookup_expr='iexact',  # Case-insensitive exact match
        help_text="Filter by exact source name (e.g., CNN, Fox News)"
    )
    
    # Bias filter
    bias = django_filters.ChoiceFilter(
        field_name='bias_label',
        choices=Article._meta.get_field('bias_label').choices,
        help_text="Filter by bias: left, center, right, unclassified"
    )
    
    # Score filters
    min_score = django_filters.NumberFilter(
        field_name='bias_score', 
        lookup_expr='gte',
        help_text="Minimum bias score (-1 to 1)"
    )
    max_score = django_filters.NumberFilter(
        field_name='bias_score', 
        lookup_expr='lte',
        help_text="Maximum bias score (-1 to 1)"
    )
    
    # Search filter (custom method)
    search = django_filters.CharFilter(
        method='filter_search',
        help_text="Search in title and content"
    )
    
    class Meta:
        model = Article
        fields = ['source_name', 'bias_label', 'is_active']
    
    def filter_search(self, queryset, name, value):
        """Search in title and content"""
        return queryset.filter(
            models.Q(title__icontains=value) | 
            models.Q(content__icontains=value)
        )