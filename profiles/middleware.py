from django.core.cache import cache
from django.http import HttpResponse
from django.conf import settings
import logging


class IPRateLimitMiddleware:
    """
    Safe version:
    - No dependency on custom settings
    - No AttributeError
    - Prevents brute force on login & signup
    """

    # Defaults (used if nothing in settings)
    DEFAULT_TIMEOUT = 60  # seconds
    DEFAULT_MAX_ATTEMPTS = 5  # attempts

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)

        # Sensitive paths to protect
        sensitive_paths = [
            "/profiles/login/",
            "/profiles/signup/",
            "/profiles/password-reset/",
        ]

        # Skip admin users & admin pages
        user = getattr(request, "user", None)
        if request.path.startswith("/admin/") or (
            user and user.is_authenticated and user.is_staff
        ):
            return self.get_response(request)

        # Only limit sensitive paths, and only on POST (actual submission
        # attempts) - counting plain GET page views meant a user could get
        # locked out just from reloading the login page a few times.
        if request.method == "POST" and any(
            request.path.startswith(p) for p in sensitive_paths
        ):
            if self.is_rate_limited(ip):
                return HttpResponse(
                    "Too many attempts. Try again later.",
                    status=429,
                    headers={"Retry-After": str(self.DEFAULT_TIMEOUT)},
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

        if attempts >= self.DEFAULT_MAX_ATTEMPTS:
            return True

        # Increase counter
        cache.set(cache_key, attempts + 1, self.DEFAULT_TIMEOUT)
        return False

    def process_exception(self, request, exception):
        logger = logging.getLogger("django.security.ratelimit")
        logger.error(
            f"Exception for IP {self.get_client_ip(request)} on path {request.path}: {str(exception)}"
        )
        return None
