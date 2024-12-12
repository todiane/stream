from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_order_confirmation_email(order):
    context = {
        'order': order,
        'user': order.user,
        'items': order.items.all(),
        'total': order.total_price,
        'site_url': settings.SITE_URL,
    }

    # Render HTML content
    html_content = render_to_string('shop/emails/order_confirmation.html', context)
    text_content = strip_tags(html_content)

    subject = f'Order Confirmation - #{order.id}'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = order.user.email

    msg = EmailMultiAlternatives(
        subject, text_content, from_email, [to_email]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def send_download_link_email(order_item):
    context = {
        'order_item': order_item,
        'user': order_item.order.user,
        'product': order_item.product,
        'download_url': order_item.product.get_download_url(),
        'site_url': settings.SITE_URL,
        'downloads_remaining': settings.MAX_DOWNLOAD_LIMIT - order_item.download_count
    }

    html_content = render_to_string('shop/emails/download_link.html', context)
    text_content = strip_tags(html_content)

    subject = f'Download Link - {order_item.product.name}'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = order_item.order.user.email

    msg = EmailMultiAlternatives(
        subject, text_content, from_email, [to_email]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()