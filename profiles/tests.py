from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .tokens import account_activation_token

class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('profiles:signup')
        self.login_url = reverse('profiles:login')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'first_name': 'Test'
        }

    def test_signup_view(self):
        # Test signup form renders
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        
        # Test user registration
        response = self.client.post(self.signup_url, self.user_data)
        self.assertEqual(response.status_code, 302)  # Should redirect after signup
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Activate your Stream English account')

    def test_password_reset(self):
        # Create a user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        
        # Request password reset
        response = self.client.post(reverse('profiles:password_reset'), {
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 302)
        
        # Check password reset email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Reset your Stream English password')

    def test_activation_token(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        token = account_activation_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Test activation link
        response = self.client.get(reverse('profiles:activate', kwargs={
            'uidb64': uid,
            'token': token
        }))
        self.assertEqual(response.status_code, 200)

    def test_unsubscribe(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        response = self.client.get(reverse('profiles:unsubscribe_email', kwargs={
            'uidb64': uid
        }))
        self.assertEqual(response.status_code, 302)  # Should redirect
        
        # Refresh user profile from database
        user.profile.refresh_from_db()
        self.assertFalse(user.profile.email_subscribed)
        