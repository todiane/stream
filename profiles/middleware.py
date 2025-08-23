# profiles/middleware.py
from django.core.cache import cache
from django.http import HttpResponse
from django.conf import settings
import logging


class IPRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)

        # Expanded list of sensitive paths
        sensitive_paths = [
            # Profile paths
            "/profiles/login/",
            "/profiles/signup/",
            "/profiles/password-reset/",
            "/profiles/activate/",
            # Admin paths
            "/admin/",
            "/admin/login/",
            "/admin/logout/",
            # CKEditor paths (since it has file upload capabilities)
            "/ckeditor/upload/",
            # Other sensitive endpoints
            "/shop/checkout/",
            "/shop/payment/",
            "/profiles/delete-account/",
        ]

        # NEW: skip rate limiting for admin users or admin paths
        user = getattr(request, "user", None)
        if request.path.startswith("/admin/") or (
            user and user.is_authenticated and (user.is_staff or user.is_superuser)
        ):
            return self.get_response(request)
        # ------------------------------------------------------------

        # Check if the current path starts with any sensitive path
        is_sensitive = any(
            request.path.startswith(sensitive_path)
            for sensitive_path in sensitive_paths
        )

        if is_sensitive:
            if self.is_rate_limited(ip):
                return HttpResponse(
                    "Too many requests. Please try again later.",
                    status=429,
                    headers={"Retry-After": str(settings.IP_RATE_LIMIT_TIMEOUT)},
                )

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

    def is_rate_limited(self, ip):
        cache_key = f"ip_rate_limit_{ip}"
        attempts = cache.get(cache_key, 0)

        if attempts >= settings.IP_RATE_LIMIT_MAX_ATTEMPTS:
            return True

        # Increment the attempts counter
        cache.set(cache_key, attempts + 1, settings.IP_RATE_LIMIT_TIMEOUT)
        return False

    def process_exception(self, request, exception):
        # Log exceptions
        logger = logging.getLogger("django.security.ratelimit")
        logger.error(
            f"Exception for IP {self.get_client_ip(request)} on path {request.path}: {str(exception)}"
        )
        return None
