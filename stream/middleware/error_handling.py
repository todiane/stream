from django.template import RequestContext


class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        # Ensure base context processors are applied
        context = RequestContext(request)
        return None  # Let Django's error handling take over
