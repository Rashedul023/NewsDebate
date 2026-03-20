# interactions/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Upvote URLs
    path('articles/<int:article_id>/upvote/', views.toggle_upvote, name='toggle-upvote'),
    path('articles/<int:article_id>/my-upvote/', views.my_upvote_status, name='my-upvote'),
    path('articles/<int:article_id>/upvotes/', views.article_upvote_count, name='upvote-count'),
    
    # Comment URLs
    path('articles/<int:article_id>/comments/', views.article_comments, name='article-comments'),
    path('comments/<int:comment_id>/', views.comment_detail, name='comment-detail'),
    path('comments/<int:comment_id>/replies/', views.comment_replies, name='comment-replies'),
    
    # Ad URLs
    path('ads/random/', views.random_ad, name='random-ad'),
    path('ads/<int:ad_id>/click/', views.track_ad_click, name='ad-click'),
    
    # Admin URLs
    path('admin/ads/performance/', views.ad_performance, name='ad-performance'),
]