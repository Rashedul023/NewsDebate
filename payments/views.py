# payments/views.py
import stripe
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta
import json
import logging

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

def get_user_from_request(request):
    """Extract user from JWT token in Authorization header"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        from users.models import User
        access_token = AccessToken(token)
        user_id = access_token.payload.get('user_id')
        return User.objects.get(id=user_id)
    except Exception:
        return None

def premium_page(request):
    """Premium pricing page"""
    return render(request, 'payments/premium.html', {
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    })

@csrf_exempt  # ← ADD THIS LINE
def create_checkout_session(request):
    """Create Stripe checkout session"""
    user = get_user_from_request(request)
    
    if not user:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': 500,
                    'product_data': {
                        'name': 'NewsDebate Premium',
                        'description': 'Ad-free experience + Support development',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/payments/success/'),
            cancel_url=request.build_absolute_uri('/payments/cancel/'),
            client_reference_id=user.id,
        )
        return JsonResponse({'sessionId': checkout_session.id})
    except Exception as e:
        logger.error(f"Stripe error: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def payment_success(request):
    """Payment success page"""
    return render(request, 'payments/success.html')

def payment_cancel(request):
    """Payment cancelled page"""
    return render(request, 'payments/cancel.html')

@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    
    try:
        event = json.loads(payload)
    except:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('client_reference_id')
        
        if user_id:
            from users.models import User
            try:
                user = User.objects.get(id=user_id)
                user.is_premium = True
                user.premium_until = timezone.now() + timedelta(days=30)
                user.save()
                logger.info(f"✅ User {user.email} upgraded to premium!")
            except User.DoesNotExist:
                logger.error(f"User {user_id} not found")
    
    return JsonResponse({'status': 'ok'})

def premium_status(request):
    """Check if user is premium"""
    user = get_user_from_request(request)
    
    if not user:
        return JsonResponse({'is_premium': False}, status=401)
    
    return JsonResponse({
        'is_premium': user.is_premium_active,
        'premium_until': user.premium_until,
    })


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    
    try:
        event = json.loads(payload)
    except:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    
    # Handle successful payment
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('client_reference_id')
        
        if user_id:
            from users.models import User
            try:
                user = User.objects.get(id=user_id)
                user.is_premium = True
                user.premium_until = timezone.now() + timedelta(days=30)
                user.save()
                logger.info(f"✅ User {user.email} upgraded to premium!")
            except User.DoesNotExist:
                logger.error(f"User {user_id} not found")
    
    return JsonResponse({'status': 'ok'})