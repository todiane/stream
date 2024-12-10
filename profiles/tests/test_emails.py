from django.test import TestCase, RequestFactory
from django.core import mail
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
from profiles.tokens import account_activation_token
from profiles.models import Profile, ContactSubmission
from profiles.utils import send_activation_email, send_welcome_activated_email, send_password_reset_email

class EmailTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='streamenglish@outlook.com',
            password='testpass123'
        )
        self.user.is_active = True
        self.user.save()
        
        # Ensure profile exists
        Profile.objects.get_or_create(user=self.user)
        
        # Create a request factory for test requests
        self.factory = RequestFactory()
        
        # Reset the outbox before each test
        mail.outbox = []

    def test_activation_email(self):
        # Test activation email sending
        token = account_activation_token.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        
        # Create a test request
        request = self.factory.get('/')
        
        response = self.client.get(reverse('profiles:activate', kwargs={
            'uidb64': uid,
            'token': token
        }))
        
        self.assertEqual(len(mail.outbox), 1)
        
        # Verify the email
        email = mail.outbox[0]
        self.assertEqual(email.to, ['streamenglish@outlook.com'])
        self.assertTrue('Activate your Stream English account' in email.subject)

    def test_welcome_email(self):
        # Create a test request
        request = self.factory.get('/')
        
        send_welcome_activated_email(request, self.user)
        
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.to, ['streamenglish@outlook.com'])
        self.assertTrue('Welcome to Stream English' in email.subject)

    def test_password_reset_email(self):
        # Create a test request
        request = self.factory.get('/')
        
        token = account_activation_token.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        
        send_password_reset_email(request, self.user, token, uid)
        
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.to, ['streamenglish@outlook.com'])
        self.assertTrue('Reset your Stream English password' in email.subject)

    def test_contact_form_email(self):
        submission = ContactSubmission.objects.create(
            user=self.user,
            reason='general',
            name='Test User',
            description='Test message'
        )
        
        subject = f'New Contact Form Submission: {submission.get_reason_display()}'
        message = f'From: {self.user.username}\nName: {submission.name}\nDescription: {submission.description}'
        
        mail.send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.CONTACT_EMAIL],
            fail_silently=False,
        )
        
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.to, ['streamenglish@outlook.com'])
        self.assertTrue('New Contact Form Submission' in email.subject)

    def test_multiple_emails_sequence(self):
        """Test that multiple emails can be sent in sequence"""
        request = self.factory.get('/')
        
        # Send activation email
        send_activation_email(request, self.user)
        self.assertEqual(len(mail.outbox), 1)
        
        # Send welcome email
        send_welcome_activated_email(request, self.user)
        self.assertEqual(len(mail.outbox), 2)
        
        # Send password reset email
        token = account_activation_token.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        send_password_reset_email(request, self.user, token, uid)
        self.assertEqual(len(mail.outbox), 3)
        