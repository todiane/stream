# stream/urls.py
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from . import views  # Add this back
from .sitemaps import StaticViewSitemap, CourseSitemap, LessonSitemap, NewsSitemap, PageSitemap
from django.views.generic import TemplateView

sitemaps = {
    'static': StaticViewSitemap,
    'courses': CourseSitemap,
    'lessons': LessonSitemap,
    'news': NewsSitemap,
    'pages': PageSitemap,
}

urlpatterns = [
    path('', include('pages.urls')),
    path("admin/", admin.site.urls),
    path('profiles/', include('profiles.urls', namespace='profiles')),
    path('courses/', include('courses.urls', namespace='courses')),
    path('news/', include('news.urls', namespace='news')),
    path('shop/', include('shop.urls', namespace='shop')),  
    path("policy/privacy/", views.privacy_view, name="privacy_policy"),
    path("policy/terms-conditions/", views.terms_view, name="terms_conditions"),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]
