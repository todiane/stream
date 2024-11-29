from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list_view, name='course_list'),
    path('<slug:course_id>/', views.course_detail_view, name='course_detail'),
    path('<slug:course_id>/lessons/<slug:lesson_id>/', views.lesson_detail_view, name='lesson_detail'),
   

    # HTMX endpoints
    path('htmx/nav-menu/', views.htmx_nav_menu, name='htmx_nav_menu'),
    path('htmx/video-modal/', views.htmx_video_modal, name='htmx_video_modal'),
    path('htmx/booking-form/', views.htmx_booking_form, name='htmx_booking_form'),
    path('htmx/latest-courses/', views.htmx_latest_courses, name='htmx_latest_courses'),
    path('htmx/submit-booking/', views.htmx_submit_booking, name='htmx_submit_booking'),
    path('htmx/load-video/', views.htmx_load_video, name='htmx_load_video'),
]