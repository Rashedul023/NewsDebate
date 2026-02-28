from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import ArticleViewSet

# Create router for automatic URL routing
router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')

# URL patterns
urlpatterns = [
    # API endpoints - USING RELATIVE URLS! (/api/articles)
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),  # Browsable API login
    
    # I'll add frontend URLs later
    # path('', views.article_list, name='article-list'),
    # path('article/<int:pk>/', views.article_detail, name='article-detail'),
]