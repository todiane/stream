from django.urls import path

from . import views

app_name = 'courses'

urlpatterns = [
    path("<slug:course_id>/lessons/<slug:lesson_id>/", views.lesson_detail_view),
    path("", views.course_list_view, name="course_list"),
    path("<slug:course_id>/enrol/", views.enrol_course, name="enrol_course"),
    path("<slug:course_id>/", views.course_detail_view, name="course_detail"),
]

