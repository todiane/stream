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

logger = logging.getLogger("django")


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
    """
    Display a lesson with YouTube video player.
    Simplified to support YouTube videos only.
    """
    try:
        course = Course.objects.get(slug=course_slug, status="publish")
        lesson_obj = Lesson.objects.get(
            course=course, slug=lesson_slug, status__in=["publish", "soon"]
        )

        # Get all lessons for navigation
        lessons = services.get_course_lessons(lesson_obj.course)
        lessons_list = list(lessons)

        # Find current position for prev/next navigation
        current_index = None
        for i, lesson in enumerate(lessons_list):
            if lesson.id == lesson_obj.id:
                current_index = i
                break

        context = {
            "object": lesson_obj,
            "course": lesson_obj.course,
            "lessons_queryset": lessons_list,
            "previous_lesson": lessons_list[current_index - 1]
            if current_index and current_index > 0
            else None,
            "next_lesson": lessons_list[current_index + 1]
            if current_index is not None and current_index < len(lessons_list) - 1
            else None,
        }

        # Extract YouTube video ID
        if lesson_obj.youtube_url:
            video_id = None
            url = lesson_obj.youtube_url

            if "youtube.com/watch?v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in url:
                video_id = url.split("/")[-1].split("?")[0]
            elif "youtube.com/embed/" in url:
                video_id = url.split("/embed/")[1].split("?")[0]

            if video_id:
                context["video_id"] = video_id
                # Set to True for lazy-loading (thumbnail click to play)
                # Set to False to load player immediately
                context["use_thumbnail_loader"] = False

        return render(request, "courses/lesson.html", context)

    except Course.DoesNotExist:
        return redirect("courses:course_list")
    except Lesson.DoesNotExist:
        return redirect("courses:course_detail", course_slug=course_slug)
    except Exception as e:
        logger.error(f"Error in lesson_detail_view: {str(e)}")
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
    # NOTE: this is the view actually wired up in urls.py. It previously just
    # re-rendered the empty form on every request - the POST handling and
    # email-sending logic lived in a second, unreferenced `booking_form`
    # function that no URL ever pointed at, so submitting the booking form
    # did nothing at all. Merged the working logic in here.
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        if name and email and message:
            try:
                send_mail(
                    subject=f"New Booking from {name}",
                    message=f"Name: {name}\nEmail: {email}\nMessage: {message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_EMAIL],
                    fail_silently=False,
                )
                messages.success(
                    request, "Thank you for your booking. We'll be in touch soon!"
                )
                return redirect("courses:booking_form")
            except Exception as e:
                logger.error(f"Error sending booking email: {e}")
                messages.error(
                    request,
                    "Sorry, something went wrong sending your booking. "
                    "Please try again or contact us directly.",
                )
        else:
            messages.error(request, "Please fill in all fields.")

    return render(request, "courses/booking/booking_form.html")
