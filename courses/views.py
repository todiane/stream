# courses/views.py

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from .models import Course, Lesson
from . import services
import logging

logger = logging.getLogger('django')


def course_list_view(request):
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        query = request.GET.get("query", "")
        # Search courses
        courses = Course.objects.filter(Q(title__icontains=query), status="publish")
        # Search lessons
        lessons = Lesson.objects.filter(
            Q(title__icontains=query),
            course__status="publish",
            status__in=["publish", "soon"],
        )

        # Combine results
        results = []
        # Add courses
        for course in courses:
            results.append(
                {"title": course.title, "path": course.path, "type": "course"}
            )
        # Add lessons
        for lesson_item in lessons:
            results.append(
                {
                    "title": lesson_item.title,
                    "path": lesson_item.get_absolute_url(),
                    "type": "lesson",
                }
            )

        return JsonResponse({"results": results})

    queryset = services.get_publish_courses()
    context = {"object_list": queryset if queryset.exists() else []}
    return render(request, "courses/list.html", context)


@login_required
def enrol_course(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    if request.method == "POST":
        if course not in request.user.profile.enrolled_courses.all():
            request.user.profile.enrolled_courses.add(course)
            messages.success(
                request, f"You have successfully enrolled in {course.title}"
            )
        else:
            messages.info(request, f"You are already enrolled in {course.title}")
    return redirect("courses:course_detail", course_slug=course_slug)


def lesson_detail_view(request, course_slug=None, lesson_slug=None, *args, **kwargs):
    try:
        course = Course.objects.get(slug=course_slug, status="publish")
        lesson_obj = Lesson.objects.get(
            course=course, 
            slug=lesson_slug, 
            status__in=["publish", "soon"]
        )
        
        context = {
            "object": lesson_obj,
            "course": lesson_obj.course,
            "lessons_queryset": services.get_course_lessons(lesson_obj.course)
        }

        if lesson_obj.youtube_url:
            if 'youtube.com/watch?v=' in lesson_obj.youtube_url:
                video_id = lesson_obj.youtube_url.split('v=')[1].split('&')[0]
            elif 'youtu.be/' in lesson_obj.youtube_url:
                video_id = lesson_obj.youtube_url.split('/')[-1]
            else:
                video_id = None
                
            if video_id:
                context["video_embed"] = f"https://www.youtube.com/embed/{video_id}?enablejsapi=1"
            
        return render(request, "courses/lesson.html", context)
        
    except Course.DoesNotExist:
        return redirect("courses:course_list")
    except Lesson.DoesNotExist:
        return redirect("courses:course_detail", course_slug=course_slug)
    except Exception as e:
        logger.error(f'Error in lesson_detail_view: {str(e)}', exc_info=True)
        return redirect("courses:course_list")
 
    
def course_detail_view(request, course_slug=None, *args, **kwargs):
    course_obj = get_object_or_404(Course, status="publish", slug=course_slug)
    lessons_queryset = services.get_course_lessons(course_obj)
    context = {
        "object": course_obj,
        "course": course_obj,
        "lessons_queryset": lessons_queryset,
        "course_description": course_obj.description if course_obj else "",
    }
    return render(request, "courses/detail.html", context)


def booking_form_view(request):
    return render(request, "courses/booking/booking_form.html")


def booking_form(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        if name and email and message:
            try:
                send_mail(
                    subject=f"New Booking from {name}",
                    message=f"Name: {name}\nEmail: {email}\nMessage: {message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_EMAIL],
                    fail_silently=False,
                )
                return render(request, "courses/booking_confirmation.html")
            except Exception as e:
                print(f"Error sending email: {e}")
        else:
            print("Missing form data")
    return render(request, "courses/booking_form.html")
