from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import Article
from .serializers import ArticleSerializer, ArticleListSerializer
from .filters import ArticleFilter

class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing political news articles.
    
    Provides:
    - List all articles (paginated, 20 per page)
    - Retrieve single article details
    - Filter by source, bias, date
    - Search in titles and content
    - Order by date or bias score
    - Statistics endpoint
    
    Examples:
    - /api/articles/ - List all articles
    - /api/articles/?source=CNN - Filter by source
    - /api/articles/?bias=left - Filter by bias
    - /api/articles/?search=election - Search articles
    - /api/articles/?ordering=-published_at - Newest first
    - /api/articles/5/ - Get article with ID 5
    - /api/articles/stats/ - Get database statistics
    """
    
    # Base queryset - only active articles, ordered by newest first
    queryset = Article.objects.filter(is_active=True).order_by('-published_at')
    
    # Filter backends
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    
    # Use our custom filter class
    filterset_class = ArticleFilter
    
    # Search fields (used by SearchFilter)
    search_fields = ['title', 'content']
    
    # Ordering fields (used by OrderingFilter)
    ordering_fields = ['published_at', 'bias_score']
    ordering = ['-published_at']  # Default ordering
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions:
        - List view: lightweight serializer (faster)
        - Detail view: full serializer (more data)
        """
        if self.action == 'list':
            return ArticleListSerializer
        return ArticleSerializer
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get database statistics.
        
        Returns:
        - Total articles count
        - Articles by source
        - Articles by bias
        - Recent activity
        """
        total = Article.objects.count()
        
        # Articles by source (top 10)
        by_source = Article.objects.values('source_name')\
            .annotate(count=Count('id'))\
            .order_by('-count')[:10]
        
        # Articles by bias
        by_bias = Article.objects.values('bias_label')\
            .annotate(count=Count('id'))\
            .order_by('bias_label')
        
        # Recent activity (last 7 days)
        last_7_days = Article.objects.filter(
            published_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Average bias score
        avg_bias = Article.objects.aggregate(Avg('bias_score'))['bias_score__avg']
        
        return Response({
            'total_articles': total,
            'last_7_days_added': last_7_days,
            'average_bias_score': round(avg_bias, 2) if avg_bias else 0,
            'by_source': list(by_source),
            'by_bias': list(by_bias),
            'timestamp': timezone.now().isoformat(),
        })
    
    @action(detail=False, methods=['get'])
    def sources(self, request):
        """
        Get list of all unique news sources.
        Useful for populating filter dropdowns in frontend.
        """
        sources = Article.objects.values_list('source_name', flat=True)\
            .distinct().order_by('source_name')
        return Response(list(sources))