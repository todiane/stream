# Save as /home/virtual/vps-cbced9/a/a588fe7474/stream/middleware/error_handling.py

import logging
import uuid
import traceback
from django.http import HttpResponseServerError
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Generate unique request ID
        request.id = str(uuid.uuid4())
        return self.get_response(request)

    def process_exception(self, request, exception):
        # Log the error with request ID
        error_details = traceback.format_exc()
        logger.error(f"Error ID {request.id}: {error_details}")

        # Prepare error context
        context = {
            "request": request,
            "error_details": error_details if settings.DEBUG else None,
            "debug": settings.DEBUG,
        }

        # Send error notification email to admins
        if not settings.DEBUG:
            self.send_error_notification(request, exception, error_details)

        # Render custom error page
        response = HttpResponseServerError(render_to_string("errors/500.html", context))
        return response

    def send_error_notification(self, request, exception, error_details):
        subject = f"[Stream English] Error ID: {request.id}"
        message = f"""
Error Details:
-------------
Error ID: {request.id}
URL: {request.build_absolute_uri()}
Method: {request.method}
User: {request.user}
IP: {request.META.get('REMOTE_ADDR')}

Exception:
----------
{str(exception)}

Traceback:
----------
{error_details}
        """

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [admin[1] for admin in settings.ADMINS],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send error notification email: {str(e)}")
