# profiles/middleware.py
from django.core.cache import cache
from django.http import HttpResponse
from django.conf import settings

class IPRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Get client IP
        ip = self.get_client_ip(request)
        
        # Define sensitive paths that need rate limiting
        sensitive_paths = [
            '/profiles/login/',
            '/profiles/signup/',
            '/profiles/password-reset/',
            '/profiles/activate/',
        ]
        
        if request.path in sensitive_paths:
            if self.is_rate_limited(ip):
                return HttpResponse(
                    "Too many requests. Please try again later.",
                    status=429  # Using standard HTTP 429 Too Many Requests
                )
        
        return self.get_response(request)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    
    def is_rate_limited(self, ip):
        cache_key = f"ip_rate_limit_{ip}"
        attempts = cache.get(cache_key, 0)
        
        if attempts >= settings.IP_RATE_LIMIT_MAX_ATTEMPTS:
            return True
            
        cache.set(
            cache_key, 
            attempts + 1, 
            settings.IP_RATE_LIMIT_TIMEOUT
        )
        return False
    