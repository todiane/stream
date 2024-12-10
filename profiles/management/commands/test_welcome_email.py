from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from profiles.tokens import account_activation_token

class Command(BaseCommand):
    help = 'Send a test welcome email to admin email'

    def handle(self, *args, **kwargs):
        try:
            # Create a test user
            test_user = User(username='TestUser')
            
            # Generate token
            token = account_activation_token.make_token(test_user)
            uid = urlsafe_base64_encode(force_bytes(1))  # Using 1 as test user ID
            
            # Get current site or use a default
            try:
                domain = Site.objects.get_current().domain
            except Site.DoesNotExist:
                domain = 'streamenglish.up.railway.app'
            
            # Create context with all required variables
            context = {
                'user': test_user,
                'domain': domain,
                'protocol': 'https',
                'email': settings.CONTACT_EMAIL,
                'unsubscribe_url': '#',
                'uid': uid,
                'token': token,
                'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS
            }

            # Render both text and HTML versions
            text_content = render_to_string('account/email/account_activation_email.txt', context)
            html_content = render_to_string('account/email/account_activation_email.html', context)

            # Create email
            subject = 'Test - Welcome to Stream English'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = settings.CONTACT_EMAIL

            try:
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                self.stdout.write(
                    self.style.SUCCESS(f'Successfully sent test email to {to_email}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to send email: {str(e)}')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to setup email test: {str(e)}')
            )
