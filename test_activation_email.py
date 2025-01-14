import os
import django
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stream.settings')
django.setup()

from django.contrib.auth.models import User
from profiles.views import send_activation_email
from django.test.client import RequestFactory
from django.http import HttpRequest

def test_activation_email():
    try:
        # Create a custom request
        class MockRequest(HttpRequest):
            def __init__(self):
                super().__init__()
                self.META = {
                    'SERVER_NAME': 'streamenglish.co.uk',
                    'SERVER_PORT': '443',
                    'HTTP_X_FORWARDED_PROTO': 'https'
                }
                self.is_secure = lambda: True

        request = MockRequest()
        
        # Get test user
        print("Getting user...")
        user = User.objects.get(username='evamandy')
        
        # Send activation email
        print("Attempting to send activation email...")
        send_activation_email(request, user)
        
        print("Activation email sent successfully!")
        
    except User.DoesNotExist:
        print("User not found! Check the username.")
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print("Full traceback:")
        print(traceback.format_exc())

if __name__ == "__main__":
    test_activation_email()