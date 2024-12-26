from django.shortcuts import redirect
from .models import URLRedirect


class RedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip processing for admin URLs
        if request.path.startswith("/admin/"):
            return self.get_response(request)

        # Check if path needs redirection
        path = request.path_info.lstrip("/")

        try:
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

        except Exception as e:
            # Log the error but don't break the site
            print(f"Error in RedirectMiddleware: {str(e)}")

        return self.get_response(request)
