from django.shortcuts import redirect
from .models import URLRedirect


class RedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if path needs redirection
        path = request.path_info.lstrip("/")

        # First try exact match
        redirect_obj = URLRedirect.objects.filter(
            old_path__iexact=path, is_active=True
        ).first()

        if not redirect_obj:
            # Try without trailing slash
            path_no_slash = path.rstrip("/")
            redirect_obj = URLRedirect.objects.filter(
                old_path__iexact=path_no_slash, is_active=True
            ).first()

        if redirect_obj:
            return redirect(redirect_obj.new_path, permanent=True)

        response = self.get_response(request)
        return response
