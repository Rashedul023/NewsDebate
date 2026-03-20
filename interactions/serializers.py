# interactions/serializers.py
from rest_framework import serializers
from .models import Upvote, Comment, Ad
from news.models import Article

# ========== Upvote Serializers ==========
class UpvoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upvote
        fields = ['id', 'user', 'article', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class UpvoteResponseSerializer(serializers.Serializer):
    """Response after upvote action"""
    upvoted = serializers.BooleanField()
    upvote_count = serializers.IntegerField()
    message = serializers.CharField(required=False)
    
class ArticleUpvoteStatusSerializer(serializers.Serializer):
    """User's upvote status for an article"""
    has_upvoted = serializers.BooleanField()
    upvote_count = serializers.IntegerField()


# ========== Comment Serializers ==========
class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'user_email', 'user_name', 'article',
            'parent', 'content', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'is_active']
    
    def get_user_name(self, obj):
        return obj.user.full_name or obj.user.get_short_name()
    
    def validate_content(self, value):
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Comment cannot be empty")
        return value.strip()

class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments"""
    class Meta:
        model = Comment
        fields = ['content', 'parent']
    
    def validate_parent(self, value):
        if value and not Comment.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Parent comment does not exist")
        return value

class CommentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating comments"""
    class Meta:
        model = Comment
        fields = ['content']
    
    def validate_content(self, value):
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Comment cannot be empty")
        return value.strip()


# ========== Ad Serializers ==========
class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ['id', 'title', 'description', 'image_url', 'link_url']