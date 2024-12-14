import os
import sys
from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

# Add your project directory to the sys.path
path = '/home/virtual/vps-cbced9/a/a588fe7474/stream'
if path not in sys.path:
    sys.path.insert(0, path)

# Add the directory containing your settings module
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Load environment variables
env_path = '/home/virtual/vps-cbced9/a/a588fe7474/stream/.env'
load_dotenv(env_path)

# Set Cloudinary environment variables explicitly
os.environ['CLOUDINARY_CLOUD_NAME'] = os.getenv('CLOUDINARY_CLOUD_NAME')
os.environ['CLOUDINARY_API_KEY'] = os.getenv('CLOUDINARY_API_KEY')
os.environ['CLOUDINARY_API_SECRET'] = os.getenv('CLOUDINARY_API_SECRET')

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stream.settings')

# Initialize Django application
application = get_wsgi_application()