from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', include('pages.urls')),
    path("admin/", admin.site.urls),
    path('profiles/', include('profiles.urls', namespace='profiles')),
    path('courses/', include('courses.urls', namespace='courses')),
    path('news/', include('news.urls', namespace='news')),
    path("policy/privacy/", views.privacy_view, name="privacy_policy"),
    path("policy/terms-conditions/", views.terms_view, name="terms_conditions"),
   path('ckeditor5/', include('django_ckeditor_5.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
