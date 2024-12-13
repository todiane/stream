# shop/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Product, Order, GuestDetails, Category
from .cart import Cart
from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import RequestFactory
import json

class ShopCheckoutTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        
        # Create test category
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        # Create test product
        self.product = Product.objects.create(
            title='Test Product',
            slug='test-product',
            category=self.category,
            price_pence=1000,  # £10.00
            status='publish'
        )
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_guest_checkout(self):
        # Add product to cart
        response = self.client.post(
            reverse('shop:cart_add', args=[self.product.id]),
            {'quantity': 1}
        )
        self.assertEqual(response.status_code, 302)

        # Test checkout page access
        response = self.client.get(reverse('shop:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/checkout.html')
        self.assertContains(response, 'Contact Details')

        # Test guest details submission
        guest_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '1234567890'
        }
        response = self.client.post(reverse('shop:checkout'), guest_data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_member_checkout(self):
        # Login
        self.client.login(username='testuser', password='testpass123')
        
        # Add product to cart
        response = self.client.post(
            reverse('shop:cart_add', args=[self.product.id]),
            {'quantity': 1}
        )
        self.assertEqual(response.status_code, 302)

        # Test checkout page access
        response = self.client.get(reverse('shop:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/checkout.html')
        self.assertNotContains(response, 'Contact Details')

    def test_cart_functions(self):
        request = self.factory.get('/')
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        
        cart = Cart(request)
        
        # Test adding item
        cart.add(self.product)
        self.assertEqual(len(cart), 1)
        
        # Test updating quantity
        cart.add(self.product, quantity=2, override_quantity=True)
        self.assertEqual(cart.cart[str(self.product.id)]['quantity'], 2)
        
        # Test removing item
        cart.remove(self.product)
        self.assertEqual(len(cart), 0)

    def test_guest_details_validation(self):
        # First add a product to the cart (required for checkout)
        response = self.client.post(
            reverse('shop:cart_add', args=[self.product.id]),
            {'quantity': 1}
        )
        self.assertEqual(response.status_code, 302)

        # Test invalid phone number
        guest_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': 'invalid123'
        }
        response = self.client.post(reverse('shop:checkout'), guest_data)
        self.assertContains(response, 'Phone number can only contain digits')

        # Test invalid email
        guest_data['phone'] = '1234567890'
        guest_data['email'] = 'invalid-email'
        response = self.client.post(reverse('shop:checkout'), guest_data)
        self.assertContains(response, 'Enter a valid email address')