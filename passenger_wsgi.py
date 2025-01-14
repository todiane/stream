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
    
    # Set up Python environment
    from stream.wsgi import application
except Exception as e:
    logging.error(f"Failed to start application: {str(e)}", exc_info=True)
    raise