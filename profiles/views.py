from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings

from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .tokens import account_activation_token
from courses.models import Course, Lesson

# Authentication views
def signup_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.profile.first_name = form.cleaned_data.get('first_name')
            user.profile.save()
            login(request, user)
            messages.success(request, 'Your account has been created! You are now logged in.')
            return redirect('profiles:profile')
    else:
        form = UserRegisterForm()
    return render(request, 'profiles/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                next_url = request.GET.get('next')
                return redirect(next_url) if next_url else redirect('profiles:profile')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        if 'next' in request.GET:
            messages.info(request, "You need to log in to enroll in this course.")
    form = AuthenticationForm()
    return render(request, 'profiles/login.html', {"form": form})

def logout_view(request):
    logout(request)
    messages.info(request, "Thank you for visiting Stream English. You are now logged out.") 
    return redirect(reverse('profiles:login'))

# Profile views
@login_required
def profile_view(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('profiles:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    profile = request.user.profile
    enrolled_courses = profile.enrolled_courses.all()
    watched_videos_count = profile.get_watched_videos_count()
    courses_completion_percentage = profile.get_courses_completion_percentage()

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'enrolled_courses': enrolled_courses,
        'watched_videos_count': watched_videos_count,
        'courses_completion_percentage': courses_completion_percentage,
    }

    return render(request, 'profiles/profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profiles:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'profiles/edit_profile.html', context)

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('home')  # Redirect to your home page
    return redirect('profiles:profile')

# Course-related views
@login_required
def enrol_course(request, course_id):
    course = get_object_or_404(Course, public_id=course_id)
    if request.method == 'POST':
        if course not in request.user.profile.enrolled_courses.all():
            request.user.profile.enrolled_courses.add(course)
            messages.success(request, f'You have successfully enrolled in {course.title}')
        else:
            messages.info(request, f'You are already enrolled in {course.title}')
    return redirect('profiles:profile')

@login_required
def resume_course(request, course_id):
    course = get_object_or_404(Course, public_id=course_id)
    profile = request.user.profile
    last_watched_lesson = profile.last_watched_lesson

    if last_watched_lesson and last_watched_lesson.course == course:
        return redirect('courses:lesson_detail', course_id=course.public_id, lesson_id=last_watched_lesson.public_id)
    else:
        first_lesson = course.lesson_set.first()
        if first_lesson:
            return redirect('courses:lesson_detail', course_id=course.public_id, lesson_id=first_lesson.public_id)
        else:
            messages.warning(request, f'No lessons available in {course.title}')
            return redirect('profiles:profile')

@login_required
def remove_course(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, public_id=course_id)
        if course in request.user.profile.enrolled_courses.all():
            request.user.profile.enrolled_courses.remove(course)
            messages.success(request, f'You have successfully unenrolled from {course.title}')
        else:
            messages.info(request, f'You are not enrolled in {course.title}')
    return redirect('profiles:profile')

# Email activation views
def send_activation_email(request, user):
    current_site = get_current_site(request)
    mail_subject = 'Activate your account.'
    message = render_to_string('accounts/email/email_confirmation_message.txt', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
        'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
    })
    to_email = user.email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse('Thank you for your email confirmation. Your account is now active.')
    else:
        return render(request, 'profiles/activation_failed.html', {'uid': uidb64, 'token': token})

def resend_activation_email(request, uidb64):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and not user.is_active:
        send_activation_email(request, user)
        messages.success(request, 'Activation email has been resent. Please check your email.')
        return redirect('profiles:login')
    else:
        messages.error(request, 'Invalid activation link or user is already active.')
        return redirect('profiles:login')

def extend_activation_time(request, uidb64):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and not user.is_active:
        extension_days = 7
        user.date_joined = timezone.now()
        user.save()
        
        send_activation_email(request, user)
        
        messages.success(request, f'Your activation period has been extended by {extension_days} days. A new activation email has been sent.')
        return redirect('profiles:login')
    else:
        messages.error(request, 'Invalid activation link or user is already active.')
        return redirect('profiles:login')

@login_required
def mark_video_watched(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    profile = request.user.profile
    profile.watched_videos.add(lesson)
    profile.last_watched_lesson = lesson
    profile.save()
    return redirect('courses:lesson_detail', course_id=lesson.course.public_id, lesson_id=lesson.public_id)