from courses.models import Course
import helpers
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages 

from . import services

def course_list_view(request):
    queryset = services.get_publish_courses()
    context = {
        "object_list": queryset
    }
    template_name = "courses/list.html"
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

def lesson_detail_view(request, course_id=None, lesson_id=None, *args, **kwargs):
    lesson_obj = services.get_lesson_detail(
        course_id=course_id,
        lesson_id=lesson_id
    )
    if lesson_obj is None:
        raise Http404
    
    email_id_exists = request.session.get('email_id')
    if lesson_obj.requires_email and not email_id_exists:
        request.session['next_url'] = request.path
        return render(request, "courses/email-required.html", {})
    
    # Get all lessons for the current course
    lessons_queryset = services.get_course_lessons(lesson_obj.course)
    
    # Get next and previous lessons
    lesson_list = list(lessons_queryset)
    current_index = lesson_list.index(lesson_obj)
    previous_lesson = lesson_list[current_index - 1] if current_index > 0 else None
    next_lesson = lesson_list[current_index + 1] if current_index < len(lesson_list) - 1 else None
    
    template_name = "courses/lesson-coming-soon.html"
    context = {
        "object": lesson_obj,
        "course": lesson_obj.course,
        "lesson": lesson_obj,
        "lessons_queryset": lessons_queryset,
        "previous_lesson": previous_lesson,
        "next_lesson": next_lesson
    }
    
    if not lesson_obj.is_coming_soon and lesson_obj.has_video:
        template_name = "courses/lesson.html"
        if lesson_obj.youtube_url:
            video_id = lesson_obj.youtube_url.split('v=')[-1]
            context['video_embed'] = f'https://www.youtube.com/embed/{video_id}'
        elif lesson_obj.video:
            video_embed_html = helpers.get_cloudinary_video_object(
                lesson_obj, 
                field_name='video',
                as_html=True,
                width=1250
            )
            context['video_embed'] = video_embed_html
    
    return render(request, template_name, context)

def course_detail_view(request, course_id=None, *args, **kwarg):
    course_obj = services.get_course_detail(course_id=course_id)
    if course_obj is None:
        raise Http404
    lessons_queryset = services.get_course_lessons(course_obj)
    context = {
        "object": course_obj,
        "course": course_obj,
        "lessons_queryset": lessons_queryset,
        "course_description": course_obj.description if course_obj else "",
    }
    return render(request, "courses/detail.html", context)

def booking_form_view(request):
    # Add any context or logic needed for the booking form
    return render(request, 'courses/booking/booking_form.html')


def booking_form(request):
    if request.method == 'POST':
        # Process form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        try:
            # Send email
            send_mail(
                subject=f'New Booking from {name}',
                message=f'Name: {name}\nEmail: {email}\nMessage: {message}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],  # Use the email from .env
                fail_silently=False,
            )
            # Return confirmation template
            return render(request, 'courses/booking_confirmation.html')
        except Exception as e:
            # Handle error
            messages.error(request, 'There was an error processing your booking.')
            
    return render(request, 'courses/booking_form.html')