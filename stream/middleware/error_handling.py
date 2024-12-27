# middleware/error_handling.py
from django.template import RequestContext
from shop.cart import Cart


class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        # Add cart to context
        request.cart = Cart(request)
        # Let Django continue with normal error handling
        return None
