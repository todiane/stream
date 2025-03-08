import logging

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log the incoming request
        logger.info(f"Incoming request: {request.method} {request.path}")
        logger.info(f"Request headers: {dict(request.headers)}")
        
        if request.method == 'POST':
            logger.info(f"POST data: {request.POST}")

        # Get the response
        response = self.get_response(request)

        # Log the response
        logger.info(f"Response status: {response.status_code}")

        return response

    def process_exception(self, request, exception):
        logger.error(f"Request failed: {exception}", exc_info=True)
        return None