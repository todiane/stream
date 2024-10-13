from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.home_view),
    path("admin/", admin.site.urls),
    path("courses/", include("courses.urls")),
    path("about/", views.about_view), 
    path("policy/privacy/", views.privacy_view),
    path("policy/terms-conditions/", views.terms_view), # Include the courses app URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
