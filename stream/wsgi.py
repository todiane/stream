import os
import sys

# Add the project directory to the Python path
path = "/home/virtual/vps-cbced9/a/a588fe7474/stream"
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stream.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
