import os
import sys
import logging

# Configure logging
logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), 'logs', 'django.log'),
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
)

try:
    # Add your site directory to the Python path
    SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, SITE_ROOT)
    
    # Set the Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stream.settings')
    
    # Set up Python environment
    from stream.wsgi import application
    
    # Wrap the application with Passenger CSRF fix
    class PassengerCSRFMiddleware:
        def __init__(self, app):
            self.app = app

        def __call__(self, environ, start_response):
            if environ.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                environ['HTTP_X_CSRF_TOKEN'] = environ.get('HTTP_X_CSRFTOKEN', '')
            return self.app(environ, start_response)

    application = PassengerCSRFMiddleware(application)
    
except Exception as e:
    logging.error(f"Failed to start application: {str(e)}", exc_info=True)
    raise