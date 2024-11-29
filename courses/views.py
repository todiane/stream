from courses.models import Course
import helpers
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from . import services

def course_list_view(request):
    queryset = services.get_publish_courses()
    context = {
        "object_list": queryset
    }
    template_name = "courses/list.html"
    if request.htmx:
        template_name = "courses/snippets/list-display.html"
        context['queryset'] = queryset[:3]
    return render(request, template_name, context)


@login_required
def enrol_course(request, course_id):
    course = get_object_or_404(Course, public_id=course_id)
    if request.method == 'POST':
        if course not in request.user.profile.enrolled_courses.all():
            request.user.profile.enrolled_courses.add(course)
            messages.success(request, f'You have successfully enrolled in {course.title}')
        else:
            messages.info(request, f'You are already enrolled in {course.title}')
    return redirect('courses:course_detail', course_id=course_id)


def course_detail_view(request, course_id=None, *args, **kwarg):
    course_obj = services.get_course_detail(course_id=course_id)
    if course_obj is None:
        raise Http404
    lessons_queryset = services.get_course_lessons(course_obj)
    context = {
        "object": course_obj,
        "lessons_queryset": lessons_queryset,
        "course_description": course_obj.description if course_obj else "",
    }
    return render(request, "courses/detail.html", context)

def lesson_detail_view(request, course_id=None, lesson_id=None, *args, **kwargs):
    print(course_id, lesson_id)
    lesson_obj = services.get_lesson_detail(
        course_id=course_id,
        lesson_id=lesson_id
    )
    if lesson_obj is None:
        raise Http404
    
    email_id_exists = request.session.get('email_id')
    if lesson_obj.requires_email and not email_id_exists:
        print(request.path)
        request.session['next_url'] = request.path
        return render(request, "courses/email-required.html", {})
    
    # Get all lessons for the current course
    lessons_queryset = services.get_course_lessons(lesson_obj.course)
    
    template_name = "courses/lesson-coming-soon.html"
    context = {
        "object": lesson_obj,
        "lessons_queryset": lessons_queryset
    }
    
    if not lesson_obj.is_coming_soon and lesson_obj.has_video:
        template_name = "courses/lesson.html"
        
        if lesson_obj.youtube_url:
            # For YouTube videos
            video_id = lesson_obj.youtube_url.split('v=')[-1]
            context['video_embed'] = f'https://www.youtube.com/embed/{video_id}'
        elif lesson_obj.video:
            # For Cloudinary videos
            video_embed_html = helpers.get_cloudinary_video_object(
                lesson_obj, 
                field_name='video',
                as_html=True,
                width=1250
            )
            context['video_embed'] = video_embed_html
    
    return render(request, template_name, context)
    print(course_id, lesson_id)
    lesson_obj = services.get_lesson_detail(
        course_id=course_id,
        lesson_id=lesson_id
    )
    if lesson_obj is None:
        raise Http404
    
    email_id_exists = request.session.get('email_id')
    if lesson_obj.requires_email and not email_id_exists:
        print(request.path)
        request.session['next_url'] = request.path
        return render(request, "courses/email-required.html", {})
    
    # Get all lessons for the current course
    lessons_queryset = services.get_course_lessons(lesson_obj.course)
    
    template_name = "courses/lesson-coming-soon.html"
    context = {
        "object": lesson_obj,
        "lessons_queryset": lessons_queryset  # Add this line
    }
    
    if not lesson_obj.is_coming_soon and lesson_obj.has_video:
        """
        Lesson is published
        Video is available
        go forward
        """
        template_name = "courses/lesson.html"
        video_embed_html = helpers.get_cloudinary_video_object(
            lesson_obj, 
            field_name='video',
            as_html=True,
            width=1250
        )
        context['video_embed'] = video_embed_html
    
    return render(request, template_name, context)


def htmx_nav_menu(request):
    return render(request, 'courses/htmx/nav_menu.html')

def htmx_video_modal(request):
    return render(request, 'courses/htmx/video_modal.html')

def htmx_booking_form(request):
    return render(request, 'courses/htmx/booking_form.html')

def htmx_latest_courses(request):
    latest_courses = services.get_publish_courses()[:3]
    return render(request, 'courses/htmx/latest_courses.html', {
        'latest_courses': latest_courses
    })

@login_required
def htmx_submit_booking(request):
    if request.method == 'POST':
        # Add your booking logic here
        return render(request, 'courses/htmx/booking_confirmation.html')
    return render(request, 'courses/htmx/booking_form.html')