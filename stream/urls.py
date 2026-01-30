# stream/urls.py
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.views.static import serve
from django.contrib.sitemaps.views import sitemap
from pages.views import home_view
from django.conf.urls.static import static

from . import views
from .sitemaps import (
    StaticViewSitemap,
    CourseSitemap,
    LessonSitemap,
    NewsSitemap,
    PageSitemap,
    ShopCategorySitemap,
    ShopProductSitemap,
    VideoSitemap,
)
from django.views.generic import TemplateView

sitemaps = {
    "static": StaticViewSitemap,
    "courses": CourseSitemap,
    "lessons": LessonSitemap,
    "news": NewsSitemap,
    "pages": PageSitemap,
    "shop_categories": ShopCategorySitemap,
    "shop_products": ShopProductSitemap,
    "videos": VideoSitemap,
}

urlpatterns = [
    path("", include("pages.urls", namespace="pages")),
    path("admin/", admin.site.urls),
    path("profiles/", include("profiles.urls", namespace="profiles")),
    path("courses/", include("courses.urls", namespace="courses")),
    path("news/", include("news.urls", namespace="news")),
    path("shop/", include("shop.urls", namespace="shop")),
    path("policy/privacy/", views.privacy_view, name="privacy_policy"),
    path("policy/cookies/", views.cookie_view, name="cookie_policy"),
    path("policy/contents/", views.content_view, name="content_policy"),
    path("policy/terms-conditions/", views.terms_view, name="terms_conditions"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots_txt",
    ),
    path(
        "media/<path:path>",
        serve,
        {
            "document_root": settings.MEDIA_ROOT,
        },
    ),
]


# Static/Media in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin customization
admin.site.site_header = "Stream English"
admin.site.site_title = "Djangify eBuilder"
admin.site.index_title = "Admin Area - Stream English"
