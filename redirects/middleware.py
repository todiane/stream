from django.shortcuts import redirect
from .models import URLRedirect


class RedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/admin/"):
            return self.get_response(request)

        # Get the path without leading slash
        path = request.path.lstrip("/")

        # Try exact match first
        redirect_obj = URLRedirect.objects.filter(
            old_path__iexact=path, is_active=True
        ).first()

        if not redirect_obj:
            # If no match, try without 'tag/' prefix
            if path.startswith("tag/"):
                path_without_tag = path[4:]
                redirect_obj = URLRedirect.objects.filter(
                    old_path__iexact=path_without_tag, is_active=True
                ).first()

        if redirect_obj:
            return redirect(f"/{redirect_obj.new_path.strip('/')}", permanent=True)

        return self.get_response(request)
