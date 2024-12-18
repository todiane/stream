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
    # Handle case where request is None (for tests)
    protocol = "https" if request and request.is_secure() else "http"
    domain = "streamenglish-co-uk.stackstaging.com"  # Default domain

    if request:
        current_site = get_current_site(request)
        domain = current_site.domain

    unsubscribe_uid = urlsafe_base64_encode(force_bytes(user.pk))
    base_url = f"{protocol}://{domain}"

    context = {
        "user": user,
        "domain": domain,
        "protocol": protocol,
        "email": user.email,
        "unsubscribe_url": f"{base_url}{reverse('profiles:unsubscribe_email', kwargs={'uidb64': unsubscribe_uid})}",
    }

    if token:
        context["token"] = token
        context["uid"] = urlsafe_base64_encode(force_bytes(user.pk))

    return context


# profiles/utils.py
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta


# profiles/utils.py
def send_activation_email(request, user):
    """Enhanced secure activation email"""
    # Check rate limiting
    try:
        check_email_throttle(user.id, "activation")
    except ValidationError as e:
        raise

    # Generate secure token with existing account_activation_token
    token = account_activation_token.make_token(user)

    # Add security headers
    email_context = get_email_context(request, user, token)
    email_context.update(
        {
            "expiry_date": datetime.now()
            + timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS),
            "ip_address": request.META.get("REMOTE_ADDR"),
            "user_agent": request.META.get("HTTP_USER_AGENT"),
        }
    )

    send_html_email(
        subject="Activate your Stream English account",
        text_template="account/email/account_activation_email.txt",
        html_template="account/email/account_activation_email.html",
        context=email_context,
        to_email=user.email,
    )


def send_welcome_activated_email(request, user):
    """
    Send welcome email after successful account activation
    """
    context = get_email_context(request, user)

    send_html_email(
        subject="Welcome to Stream English!",
        text_template="account/email/welcome_activated.txt",
        html_template="account/email/welcome_activated.html",
        context=context,
        to_email=user.email,
    )


def send_password_reset_email(request, user, token, uid):
    """
    Send password reset email
    """
    context = get_email_context(request, user)
    context.update({"token": token, "uid": uid})

    send_html_email(
        subject="Reset your Stream English password",
        text_template="account/email/password_reset_email.txt",
        html_template="account/email/password_reset_email.html",
        context=context,
        to_email=user.email,
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
            f"Too many {action} attempts. Please wait {timeout//60} minutes before trying again."
        )

    cache.set(cache_key, attempts + 1, timeout)


def send_admin_notification(subject, message):
    """
    Send a simple notification email to admin
    """
    from django.core.mail import send_mail
    from django.conf import settings
    import logging

    logger = logging.getLogger(__name__)

    try:
        print(
            f"Attempting to send admin notification to {settings.CONTACT_EMAIL}"
        )  # Debug print
        # Try sending with settings.CONTACT_EMAIL
        result = send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.CONTACT_EMAIL],
            fail_silently=False,
        )

        # If successful, try sending to hardcoded email as backup
        if result:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                ["streamenglish@outlook.com"],
                fail_silently=True,
            )

        print(f"Admin notification sent successfully: {subject} (Result: {result})")
        return True
    except Exception as e:
        print(f"Failed to send admin notification: {str(e)}")
        return False
