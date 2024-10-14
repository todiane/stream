from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("admin/", admin.site.urls),
    path("courses/", include("courses.urls")),
    path("about/", views.about_view, name="about"),
    path("policy/privacy/", views.privacy_view, name="privacy_policy"),
    path("policy/terms-conditions/", views.terms_view, name="terms_conditions"),
    path("accounts/", include("allauth.urls")), 
    path('profiles/', include('profiles.urls')),
      # Add this line if you're using django-allauth
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]