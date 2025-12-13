from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.cache import cache
from django.conf import settings
from django.contrib.sites.models import Site


class ProductionSmokeTests(TestCase):
    def test_cache_backend(self):
        cache.set("health", "ok", 5)
        self.assertEqual(cache.get("health"), "ok")

    def test_admin_login_page_loads(self):
        response = self.client.get(
            reverse("admin:login"),
            follow=True,
            secure=True,
        )
        self.assertEqual(response.status_code, 200)

    def test_admin_index_for_staff(self):
        user = User.objects.create_superuser(
            username="admin_test",
            email="admin@test.com",
            password="testpass123",
        )
        self.client.login(username="admin_test", password="testpass123")

        response = self.client.get(
            reverse("admin:index"),
            follow=True,
            secure=True,
        )
        self.assertEqual(response.status_code, 200)


class SiteConfigurationTests(TestCase):
    def test_site_id_exists(self):
        """
        Fails if SITE_ID points to a Site that does not exist.
        This catches admin/login and CurrentSiteMiddleware breakage.
        """
        self.assertTrue(
            Site.objects.filter(id=settings.SITE_ID).exists(),
            f"SITE_ID={settings.SITE_ID} does not exist in django_site table",
        )
