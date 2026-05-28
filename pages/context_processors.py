# pages/context_processors.py


def site_settings(request):
    """
    Injects the SiteSettings singleton into every template context as
    ``site_settings``.  A try/except guard prevents errors on a fresh
    install before migrations have been run.
    """
    try:
        from .models import SiteSettings

        return {"site_settings": SiteSettings.get()}
    except Exception:
        return {"site_settings": None}
