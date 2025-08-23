# profiles/utils.py
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
from datetime import datetime, timedelta
from django.core.cache import cache
from django.core.exceptions import ValidationError
from .tokens import account_activation_token
import logging

logger = logging.getLogger(__name__)


def get_email_context(request, user, token=None):
    """Generate common context for email templates"""
    protocol = "https" if request and request.is_secure() else "http"
    domain = "streamenglish.co.uk"  # Default domain

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


def send_activation_email(request, user):
    """Enhanced secure activation email"""
    try:
        check_email_throttle(user.id, "activation")

        # Generate secure token
        token = account_activation_token.make_token(user)
        logger.debug(f"Generated activation token for {user.username}: {token}")

        # Get context with security headers
        email_context = get_email_context(request, user, token)
        email_context.update(
            {
                "expiry_date": datetime.now()
                + timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS),
                "ip_address": request.META.get("REMOTE_ADDR"),
                "user_agent": request.META.get("HTTP_USER_AGENT"),
            }
        )

        # Render email content
        text_content = render_to_string(
            "account/email/account_activation_email.txt", email_context
        )
        html_content = render_to_string(
            "account/email/account_activation_email.html", email_context
        )

        # Create and send email
        msg = EmailMultiAlternatives(
            "Activate your Stream English account",
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"Activation email sent to {user.email} with token {token}")

    except Exception as e:
        logger.error(f"Failed to send activation email to {user.email}: {str(e)}")
        raise


def send_welcome_activated_email(request, user):
    """Send welcome email after successful account activation"""
    try:
        context = get_email_context(request, user)
        text_content = render_to_string("account/email/welcome_activated.txt", context)
        html_content = render_to_string("account/email/welcome_activated.html", context)

        msg = EmailMultiAlternatives(
            "Welcome to Stream English!",
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"Welcome email sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        raise


def send_password_reset_email(request, user, token, uid):
    """Send password reset email"""
    try:
        context = get_email_context(request, user)
        context.update({"token": token, "uid": uid})

        text_content = render_to_string(
            "account/email/password_reset_email.txt", context
        )
        html_content = render_to_string(
            "account/email/password_reset_email.html", context
        )

        msg = EmailMultiAlternatives(
            "Reset your Stream English password",
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"Password reset email sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        raise


# Cache utilities
def get_cache_key(user_id, action):
    return f"email_attempt_{action}_{user_id}"


def check_email_throttle(user_id, action, max_attempts=3, timeout=300):
    """Prevent email spam by limiting attempts"""
    cache_key = get_cache_key(user_id, action)
    attempts = cache.get(cache_key, 0)

    if attempts >= max_attempts:
        raise ValidationError(
            f"Too many {action} attempts. Please wait {timeout // 60} minutes before trying again."
        )

    cache.set(cache_key, attempts + 1, timeout)
