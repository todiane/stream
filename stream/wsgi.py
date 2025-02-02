"""
WSGI config for stream project.
"""
import os
import sys

# Set the path to your virtualenv
VIRTUALENV_PATH = '/home/str3a3eng24/virtualenv/stream/3.10'
if VIRTUALENV_PATH not in sys.path:
    sys.path.insert(0, VIRTUALENV_PATH)

# Add site-packages from virtualenv
site_packages = os.path.join(VIRTUALENV_PATH, 'lib', 'python3.10', 'site-packages')
if site_packages not in sys.path:
    sys.path.insert(0, site_packages)

# Add the Django project directory to the Python path
project_path = '/home/str3a3eng24/stream'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Add the directory containing the project to the Python path
parent_path = '/home/str3a3eng24'
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stream.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()