import os
from django.core.wsgi import get_wsgi_application

# Only set a default. Allow overrides by manage.py or gunicorn.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stream.settings.production")

application = get_wsgi_application()
