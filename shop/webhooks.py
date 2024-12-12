import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Order

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        handle_payment_intent_succeeded(payment_intent)
    elif event.type == 'payment_intent.payment_failed':
        payment_intent = event.data.object
        handle_payment_intent_failed(payment_intent)

    return HttpResponse(status=200)

def handle_payment_intent_succeeded(payment_intent):
    user_id = payment_intent.metadata.get('user_id')
    order = Order.objects.filter(
        user_id=user_id,
        payment_intent_id=payment_intent.id,
        status='pending'
    ).first()
    
    if order:
        order.status = 'completed'
        order.save()

def handle_payment_intent_failed(payment_intent):
    user_id = payment_intent.metadata.get('user_id')
    order = Order.objects.filter(
        user_id=user_id,
        payment_intent_id=payment_intent.id,
        status='pending'
    ).first()
    
    if order:
        order.status = 'failed'
        order.save()
