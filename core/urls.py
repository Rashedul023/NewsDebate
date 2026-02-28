"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from datetime import datetime

def home(request):
    """Home page showing API is working"""
    return JsonResponse({
        'message': 'NewsDebate API is running!',
        'api_endpoints': {
            'articles': '/api/articles/',
            'article_detail': '/api/articles/{id}/',
            'stats': '/api/articles/stats/',
            'sources': '/api/articles/sources/',
        },
        'docs': 'Visit /api/articles/ in browser to test',
        'timestamp': datetime.now().isoformat(),
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),  # Home page
    path('', include('news.urls')),  # Include news app URLs
]