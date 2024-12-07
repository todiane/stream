# profiles/utils.py
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
from datetime import datetime, timedelta
from .tokens import account_activation_token


def send_html_email(subject, text_template, html_template, context, to_email):
    """
    Generic function to send HTML emails with text alternative
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    text_content = render_to_string(text_template, context)
    html_content = render_to_string(html_template, context)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def get_email_context(request, user, token=None):
    """
    Generate common context for email templates
    """
    current_site = get_current_site(request)
    unsubscribe_uid = urlsafe_base64_encode(force_bytes(user.pk))
    context = {
        'user': user,
        'domain': current_site.domain,
        'protocol': 'https' if request.is_secure() else 'http',
        'email': user.email,
        'unsubscribe_url': f"{request.scheme}://{current_site.domain}{reverse('profiles:unsubscribe_email', kwargs={'uidb64': unsubscribe_uid})}"
    }
    
    if token:
        context['token'] = token
        context['uid'] = urlsafe_base64_encode(force_bytes(user.pk))
    
    return context

# profiles/utils.py
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta


# profiles/utils.py
def send_activation_email(request, user):
    """Enhanced secure activation email"""
    # Check rate limiting
    try:
        check_email_throttle(user.id, 'activation')
    except ValidationError as e:
        raise

    # Generate secure token with existing account_activation_token
    token = account_activation_token.make_token(user)
    
    # Add security headers
    email_context = get_email_context(request, user, token)
    email_context.update({
        'expiry_date': datetime.now() + timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS),
        'ip_address': request.META.get('REMOTE_ADDR'),
        'user_agent': request.META.get('HTTP_USER_AGENT')
    })

    send_html_email(
        subject='Activate your Stream English account',
        text_template='account/email/account_activation_email.txt',
        html_template='account/email/account_activation_email.html',
        context=email_context,
        to_email=user.email
    )

def send_password_reset_email(request, user, token, uid):
    """
    Send password reset email
    """
    context = get_email_context(request, user)
    context.update({
        'token': token,
        'uid': uid
    })
    
    send_html_email(
        subject='Reset your Stream English password',
        text_template='account/email/password_reset_email.txt',
        html_template='account/email/password_reset_email.html',
        context=context,
        to_email=user.email
    )

# profiles/utils.py
from django.core.cache import cache
from django.core.exceptions import ValidationError

def get_cache_key(user_id, action):
    return f"email_attempt_{action}_{user_id}"

def check_email_throttle(user_id, action, max_attempts=3, timeout=300):
    """
    Prevent email spam by limiting attempts
    max_attempts: Maximum attempts allowed
    timeout: Time in seconds before counter resets
    """
    cache_key = get_cache_key(user_id, action)
    attempts = cache.get(cache_key, 0)
    
    if attempts >= max_attempts:
        raise ValidationError(
            f'Too many {action} attempts. Please wait {timeout//60} minutes before trying again.'
        )
    
    cache.set(cache_key, attempts + 1, timeout)
