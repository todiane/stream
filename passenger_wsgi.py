import os
import sys

# Add your Django project directory to the Python path
sys.path.insert(0, "/home/virtual/vps-cbced9/a/a588fe7474/stream")

# Set Django settings module
os.environ["DJANGO_SETTINGS_MODULE"] = "stream.settings"

# Import and create WSGI application
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
