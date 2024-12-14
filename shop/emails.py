from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_order_confirmation_email(order):
    # Prepare serializable order items data
    items_data = [{
        'name': item.product.title,
        'price': item.price_paid_pence / 100,  # Convert back to pounds/dollars
        'quantity': item.quantity,
        'downloads_remaining': item.downloads_remaining
    } for item in order.items.all()]

    context = {
        'order_id': order.order_id,
        'email': order.email,
        'items': items_data,
        'total': order.total_price,
        'site_url': settings.SITE_URL,
        'user_name': order.user.get_full_name() if order.user else None,
        'date_created': order.created.strftime('%Y-%m-%d %H:%M:%S')
    }

    # Render HTML content
    html_content = render_to_string('account/email/order_confirmation.html', context)
    text_content = strip_tags(html_content)

    # Send email
    subject = f'Order Confirmation #{order.order_id}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [order.email]

    msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def send_download_link_email(order_item):
    context = {
        'order_item': order_item,
        'user': order_item.order.user,
        'product': order_item.product,
        'download_url': order_item.product.get_download_url(),
        'site_url': settings.SITE_URL,
        'downloads_remaining': settings.SHOP_SETTINGS['MAX_DOWNLOAD_ATTEMPTS'] - order_item.download_count
    }

    html_content = render_to_string('account/email/download_link.html', context)
    text_content = strip_tags(html_content)

    subject = f'Download Link - {order_item.product.title}'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = order_item.order.user.email

    msg = EmailMultiAlternatives(
        subject, text_content, from_email, [to_email]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
