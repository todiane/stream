# stream/views.py
from django.shortcuts import render
from courses import services
from django.core.mail import send_mail
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
import logging

app_name = "stream"

logger = logging.getLogger(__name__)


def home_view(request, *args, **kwargs):
    queryset = services.get_publish_courses()
    context = {"object_list": queryset[:3]}  # Get first 3 published courses
    template_name = "home.html"
    return render(request, template_name, context)


def about_view(request):
    template_name = "about.html"
    return render(request, template_name)


def privacy_view(request):
    template_name = "policy/privacy.html"
    return render(request, template_name)


def terms_view(request):
    template_name = "policy/terms-conditions.html"
    return render(request, template_name)


def cookie_view(request):
    template_name = "policy/cookies.html"
    return render(request, template_name)
