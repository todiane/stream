# middleware/csrf_debug.py

import logging

logger = logging.getLogger('django')

class CSRFDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Simple, safe logging
            logger.info("Path: %s", request.path)
            logger.info("CSRF Cookie Present: %s", 'csrftoken' in request.COOKIES)
            
            response = self.get_response(request)
            return response
            
        except Exception as e:
            # Log any errors but don't crash
            logger.error("CSRF middleware error: %s", str(e))
            return self.get_response(request)
