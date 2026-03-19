from django.contrib import admin
from .models import Upvote, Comment, Ad

@admin.register(Upvote)
class UpvoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'article', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'article__title']
    raw_id_fields = ['user', 'article']
    date_hierarchy = 'created_at'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'article', 'content_preview', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__email', 'content', 'article__title']
    raw_id_fields = ['user', 'article', 'parent']
    date_hierarchy = 'created_at'
    actions = ['approve_comments', 'hide_comments']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    def approve_comments(self, request, queryset):
        queryset.update(is_active=True)
    approve_comments.short_description = "Approve selected comments"
    
    def hide_comments(self, request, queryset):
        queryset.update(is_active=False)
    hide_comments.short_description = "Hide selected comments"

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'view_count', 'click_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'priority']
    search_fields = ['title', 'description']
    list_editable = ['priority', 'is_active']
    readonly_fields = ['view_count', 'click_count']
    fieldsets = (
        ('Ad Content', {
            'fields': ('title', 'description', 'image_url', 'link_url')
        }),
        ('Performance', {
            'fields': ('view_count', 'click_count'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_active', 'priority')
        }),
    )