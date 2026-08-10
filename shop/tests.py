# shop/tests.py
#
# NOTE: this file previously imported a `GuestDetails` model and tested a
# guest-checkout flow (contact details form, phone/email validation) that no
# longer exists in models.py - checkout is now login-required and goes
# straight to Stripe. That made the whole module fail to import, so none of
# these tests were actually running. Rewritten to match current behaviour.
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import RequestFactory

from .models import Product, Order, OrderItem, Category
from .cart import Cart


@override_settings(SECURE_SSL_REDIRECT=False)
class ShopCheckoutTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

        self.category = Category.objects.create(
            name="Test Category", slug="test-category"
        )

        self.product = Product.objects.create(
            title="Test Product",
            slug="test-product",
            category=self.category,
            price_pence=1000,  # £10.00
            status="publish",
        )

        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_checkout_requires_login(self):
        # Anonymous users should be redirected to login, not allowed through
        # to checkout.
        self.client.post(
            reverse("shop:cart_add", args=[self.product.id]), {"quantity": 1}
        )
        response = self.client.get(reverse("shop:checkout"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("profiles:login"), response.url)

    @patch("shop.views.stripe.PaymentIntent.create")
    def test_member_checkout(self, mock_create):
        mock_create.return_value = MagicMock(
            id="pi_test_123", client_secret="pi_test_123_secret"
        )

        self.client.login(username="testuser", password="testpass123")

        response = self.client.post(
            reverse("shop:cart_add", args=[self.product.id]), {"quantity": 1}
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse("shop:checkout"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shop/checkout.html")

        # An Order and OrderItem should have been created (pending, unpaid)
        # ready for Stripe to confirm via the webhook.
        order = Order.objects.filter(user=self.user).first()
        self.assertIsNotNone(order)
        self.assertFalse(order.paid)
        self.assertEqual(order.items.count(), 1)

    def test_cart_functions(self):
        request = self.factory.get("/")
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()

        cart = Cart(request)

        # Test adding item
        cart.add(self.product)
        self.assertEqual(len(cart), 1)

        # Test updating quantity
        cart.add(self.product, quantity=2, override_quantity=True)
        self.assertEqual(cart.cart[str(self.product.id)]["quantity"], 2)

        # Test removing item
        cart.remove(self.product)
        self.assertEqual(len(cart), 0)

    def test_cart_uses_sale_price_when_available(self):
        sale_product = Product.objects.create(
            title="Sale Product",
            slug="sale-product",
            category=self.category,
            price_pence=1000,
            sale_price_pence=500,
            status="publish",
        )

        request = self.factory.get("/")
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()

        cart = Cart(request)
        cart.add(sale_product)

        self.assertEqual(
            Decimal(cart.cart[str(sale_product.id)]["price"]), Decimal("5.00")
        )

    def test_secure_download_requires_paid_order(self):
        self.client.login(username="testuser", password="testpass123")

        order = Order.objects.create(
            user=self.user, email=self.user.email, paid=False, status="pending"
        )
        order_item = OrderItem.objects.create(
            order=order, product=self.product, price_paid_pence=1000
        )

        response = self.client.get(
            reverse("shop:secure_download", args=[order_item.id])
        )
        # Unpaid orders must not be downloadable.
        self.assertRedirects(response, reverse("shop:order_history"))
