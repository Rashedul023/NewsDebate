from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'source_name', 'bias_label', 'bias_score', 'published_at']
    list_filter = ['bias_label', 'source_name', 'published_at']
    search_fields = ['title', 'content']
    date_hierarchy = 'published_at'
    readonly_fields = ['fetched_at']
    
    fieldsets = (
        ('Article Information', {
            'fields': ('title', 'content', 'image_url', 'url')
        }),
        ('Source', {
            'fields': ('source_name', 'published_at')
        }),
        ('Bias Detection (Future ML)', {
            'fields': ('bias_label', 'bias_score'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('fetched_at', 'is_active'),
            'classes': ('collapse',)
        }),
    )