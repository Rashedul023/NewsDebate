# interactions/views.py
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db.models import Q

from news.models import Article
from .models import Upvote, Comment, Ad
from .serializers import (
    UpvoteResponseSerializer, ArticleUpvoteStatusSerializer,
    CommentSerializer, CommentCreateSerializer, CommentUpdateSerializer,
    AdSerializer
)


# ========== Upvote Views ==========
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_upvote(request, article_id):
    """
    Toggle upvote for an article.
    
    POST /api/articles/{id}/upvote/
    """
    article = get_object_or_404(Article, id=article_id, is_active=True)
    user = request.user
    
    try:
        # Check if upvote exists
        upvote = Upvote.objects.get(user=user, article=article)
        # If exists, delete it
        upvote.delete()
        upvoted = False
        message = "Upvote removed"
    except Upvote.DoesNotExist:
        # If doesn't exist, create it
        try:
            Upvote.objects.create(user=user, article=article)
            upvoted = True
            message = "Upvote added"
        except IntegrityError:
            return Response(
                {'error': 'Could not process upvote'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Update article's upvote count
    article.upvote_count = article.upvotes.count()
    article.save(update_fields=['upvote_count'])
    
    response_data = {
        'upvoted': upvoted,
        'upvote_count': article.upvote_count,
        'message': message
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_upvote_status(request, article_id):
    """
    Check if current user has upvoted an article.
    
    GET /api/articles/{id}/my-upvote/
    """
    article = get_object_or_404(Article, id=article_id, is_active=True)
    user = request.user
    
    has_upvoted = Upvote.objects.filter(user=user, article=article).exists()
    
    response_data = {
        'has_upvoted': has_upvoted,
        'upvote_count': article.upvote_count
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def article_upvote_count(request, article_id):
    """
    Get upvote count for an article (public).
    
    GET /api/articles/{id}/upvotes/
    """
    article = get_object_or_404(Article, id=article_id, is_active=True)
    
    return Response({
        'article_id': article.id,
        'upvote_count': article.upvote_count
    }, status=status.HTTP_200_OK)


# ========== Comment Views ==========
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def article_comments(request, article_id):
    """
    List all comments for an article or create a new comment.
    
    GET  /api/articles/{id}/comments/ - List comments
    POST /api/articles/{id}/comments/ - Create comment
    """
    article = get_object_or_404(Article, id=article_id, is_active=True)
    
    if request.method == 'GET':
        comments = Comment.objects.filter(
            article=article, 
            is_active=True,
            parent__isnull=True  # Only top-level comments
        ).select_related('user').prefetch_related('replies')
        
        serializer = CommentSerializer(comments, many=True)
        return Response({
            'count': comments.count(),
            'results': serializer.data
        })
    
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = CommentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        comment = Comment.objects.create(
            user=request.user,
            article=article,
            content=serializer.validated_data['content'],
            parent=serializer.validated_data.get('parent')
        )
        
        # Update article comment count
        article.comment_count = article.comments.filter(is_active=True).count()
        article.save(update_fields=['comment_count'])
        
        response_serializer = CommentSerializer(comment)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def comment_detail(request, comment_id):
    """
    Retrieve, update, or delete a comment.
    
    GET    /api/comments/{id}/ - Get comment
    PUT    /api/comments/{id}/ - Update comment
    DELETE /api/comments/{id}/ - Delete comment
    """
    comment = get_object_or_404(Comment, id=comment_id, is_active=True)
    
    # Check ownership
    if comment.user != request.user and not request.user.is_staff:
        return Response(
            {'error': 'You do not have permission to modify this comment'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'GET':
        serializer = CommentSerializer(comment)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = CommentUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        comment.content = serializer.validated_data['content']
        comment.save()
        
        response_serializer = CommentSerializer(comment)
        return Response(response_serializer.data)
    
    elif request.method == 'DELETE':
        # Soft delete
        comment.is_active = False
        comment.save()
        
        # Update article comment count
        article = comment.article
        article.comment_count = article.comments.filter(is_active=True).count()
        article.save(update_fields=['comment_count'])
        
        return Response(
            {'message': 'Comment deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def comment_replies(request, comment_id):
    """
    Get replies to a comment.
    
    GET /api/comments/{id}/replies/
    """
    parent = get_object_or_404(Comment, id=comment_id, is_active=True)
    replies = Comment.objects.filter(parent=parent, is_active=True).select_related('user')
    
    serializer = CommentSerializer(replies, many=True)
    return Response({
        'count': replies.count(),
        'results': serializer.data
    })


# ========== Ad Views ==========
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def random_ad(request):
    """
    Get a random active ad.
    Returns no ad if user is premium.
    
    GET /api/ads/random/
    """
    user = request.user
    
    # Check if user is premium
    if user.is_authenticated and user.is_premium_active:
        return Response({'ad': None, 'show_ad': False})
    
    # Get random ad
    ads = Ad.objects.filter(is_active=True)
    
    if not ads.exists():
        return Response({'ad': None, 'show_ad': False})
    
    # Simple random selection
    ad = ads.order_by('?').first()
    
    # Track view
    ad.view_count += 1
    ad.save(update_fields=['view_count'])
    
    serializer = AdSerializer(ad)
    return Response({
        'ad': serializer.data,
        'show_ad': True
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def track_ad_click(request, ad_id):
    """
    Track when a user clicks on an ad.
    
    POST /api/ads/{id}/click/
    """
    ad = get_object_or_404(Ad, id=ad_id, is_active=True)
    
    ad.click_count += 1
    ad.save(update_fields=['click_count'])
    
    return Response({'message': 'Click tracked'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def ad_performance(request):
    """
    Admin view to see ad performance metrics.
    
    GET /api/admin/ads/performance/
    """
    ads = Ad.objects.all().values(
        'id', 'title', 'view_count', 'click_count', 'priority', 'is_active'
    ).order_by('-view_count')
    
    performance_data = []
    for ad in ads:
        ctr = (ad['click_count'] / ad['view_count'] * 100) if ad['view_count'] > 0 else 0
        performance_data.append({
            **ad,
            'ctr': round(ctr, 2),
            'clicks_per_view': f"{ad['click_count']}/{ad['view_count']}"
        })
    
    return Response(performance_data)