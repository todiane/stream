import stripe
import logging
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Order
from .emails import fulfil_order

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return HttpResponse(status=400)

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "payment_intent.succeeded":
        _handle_payment_intent_succeeded(data)

    elif event_type == "payment_intent.payment_failed":
        _handle_payment_intent_failed(data)

    return HttpResponse(status=200)


def _handle_payment_intent_succeeded(payment_intent):
    payment_intent_id = payment_intent.id

    order = Order.objects.filter(payment_intent_id=payment_intent_id).first()
    if not order:
        logger.error(f"Order not found for PaymentIntent {payment_intent_id}")
        return

    if order.paid:
        logger.info(f"Order {order.order_id} already completed. Skipping.")
        return

    logger.info(f"Completing order {order.order_id}")

    order.paid = True
    order.status = "completed"
    order.save()

    # Bump purchase counts and send download-link + confirmation emails
    fulfil_order(order)


def _handle_payment_intent_failed(payment_intent):
    payment_intent_id = payment_intent.id

    order = Order.objects.filter(payment_intent_id=payment_intent_id).first()
    if not order:
        return

    order.status = "failed"
    order.save()
