from django.shortcuts import redirect
from .models import URLRedirect
import re


class RedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def clean_path(self, path):
        """Clean the path by removing unnecessary prefixes and standardizing format"""
        # Remove leading/trailing slashes
        path = path.strip("/")

        # Remove date patterns (YYYY/MM/DD)
        path = re.sub(r"\d{4}/\d{2}/\d{2}/", "", path)

        # Remove 'tag/' prefix if present
        if path.startswith("tag/"):
            path = path[4:]

        return path

    def __call__(self, request):
        # Skip processing for admin URLs
        if request.path.startswith("/admin/"):
            return self.get_response(request)

        # Get the path and clean it
        original_path = request.path_info.lstrip("/")
        cleaned_path = self.clean_path(original_path)

        try:
            # Try to find a redirect using various path formats
            redirect_obj = (
                URLRedirect.objects.filter(
                    old_path__iexact=original_path, is_active=True
                ).first()
                or URLRedirect.objects.filter(
                    old_path__iexact=cleaned_path, is_active=True
                ).first()
                or URLRedirect.objects.filter(
                    old_path__iexact=original_path.rstrip("/"), is_active=True
                ).first()
                or URLRedirect.objects.filter(
                    old_path__iexact=original_path.strip("/"), is_active=True
                ).first()
            )

            if redirect_obj:
                # Ensure the new path starts with a forward slash and ends with one if original did
                new_path = f"/{redirect_obj.new_path.strip('/')}"
                if original_path.endswith("/"):
                    new_path = f"{new_path}/"
                return redirect(new_path, permanent=True)

        except Exception as e:
            # Log the error properly
            import logging

            logger = logging.getLogger("django")
            logger.error(f"Error in RedirectMiddleware: {str(e)}")

        return self.get_response(request)
