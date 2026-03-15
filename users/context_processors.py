from .models import User

def auth_context(request):
    """Add authentication context to all templates"""
    return {
        'user': request.user if request.user.is_authenticated else None,
    }