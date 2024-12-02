# courses/urls.py
from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list_view, name='course_list'),
    path('booking-form/', views.booking_form_view, name='booking_form'),
    path('<slug:course_slug>/', views.course_detail_view, name='course_detail'),
    path('<slug:course_slug>/lessons/<slug:lesson_slug>/', views.lesson_detail_view, name='lesson_detail'),
]