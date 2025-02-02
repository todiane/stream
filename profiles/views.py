# profiles/views.py
from email.message import EmailMessage
import logging
from django.core.mail import get_connection
from profiles.models import Profile, VideoProgress
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .utils import (
    send_admin_notification,
    send_welcome_activated_email,
)
from .utils import check_email_throttle
from django.conf import settings
from django.views.generic.edit import FormView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .forms import ContactForm
from .forms import CustomPasswordResetForm
from .tokens import account_activation_token
from courses.models import Course, Lesson
import json 

logger = logging.getLogger(__name__)

def signup_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            try:
                # Create user first
                user = form.save(commit=False)
                user.is_active = True
                user.save()

                # Create or update profile
                profile, created = Profile.objects.get_or_create(user=user)
                profile.first_name = form.cleaned_data.get("first_name")
                profile.email_verified = False
                profile.save()

                # Try to send activation email
                try:
                    current_site = get_current_site(request)
                    subject = "Activate your Stream English Account"
                    unsubscribe_uid = urlsafe_base64_encode(force_bytes(user.pk))

                    print("Attempting to send activation email...")
                    token = account_activation_token.make_token(user)
                    print(f"Generated token: {token}")  # Keep this debug line
                    token = account_activation_token.make_token(user)
                    logger.info(f"[Token Debug] Generated signup token for {user.username}: {token}")
                    context = {
                        "user": user,
                        "domain": "streamenglish.co.uk",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": token,  # Use the same token we just generated
                        "protocol": "https",
                        "expiration_days": settings.ACCOUNT_ACTIVATION_DAYS,
                        "email": user.email,
                        "unsubscribe_url": f"https://streamenglish.co.uk{reverse('profiles:unsubscribe_email', kwargs={'uidb64': unsubscribe_uid})}",
                    }
                    logger.info(f"[Token Debug] Using token in email context: {context['token']}")
  
                    html_message = render_to_string(
                        "account/email/account_activation_email.html", context
                    )
                    text_message = render_to_string(
                        "account/email/account_activation_email.txt", context
                    )

                    msg = EmailMultiAlternatives(
                        subject, text_message, settings.DEFAULT_FROM_EMAIL, [user.email]
                    )
                    msg.attach_alternative(html_message, "text/html")
                    msg.send()
                    print("Activation email sent successfully!")

                except Exception as e:
                    # Log the specific email error but don't prevent registration
                    logger.error(f"Failed to send activation email: {str(e)}")
                    messages.warning(
                        request,
                        "Your account was created but there was an error sending the activation email. "
                        "You can still log in, but you'll need to verify your email to access all features.",
                    )
                    return redirect("profiles:login")

                messages.success(
                    request,
                    "Registration successful! Please check your email to activate your account. "
                    "You can still log in, but some features require email verification.",
                )
                return redirect("profiles:login")

            except Exception as e:
                # Log any other errors during user creation
                logger.error(f"Error during user registration: {str(e)}")
                messages.error(
                    request,
                    "There was an error creating your account. Please try again.",
                )
                return render(request, "profiles/signup.html", {"form": form})
    else:
        form = UserRegisterForm()

    return render(request, "profiles/signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                next_url = request.GET.get("next")
                return redirect(next_url) if next_url else redirect("profiles:profile")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        if "next" in request.GET:
            messages.info(request, "You need to log in to enrol in this course.")
    form = AuthenticationForm()
    return render(request, "profiles/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(
        request, "Thank you for visiting Stream English. You are now logged out."
    )
    return redirect(reverse("profiles:login"))


# Profile views
@login_required
def profile_view(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your account has been updated!")
            return redirect("profiles:profile")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    profile = request.user.profile
    enrolled_courses = profile.enrolled_courses.all()
    watched_videos_count = profile.get_watched_videos_count()

    courses_with_progress = []
    for course in enrolled_courses:
        progress = profile.get_course_completion_percentage(course)
        courses_with_progress.append({"course": course, "progress": progress})

    context = {
        "u_form": u_form,
        "p_form": p_form,
        "enrolled_courses": enrolled_courses,
        "courses_with_progress": courses_with_progress,
        "watched_videos_count": watched_videos_count,
        "overall_progress": profile.get_courses_completion_percentage(),
        "contact_form": ContactForm(),
    }

    context.update(
        {
            "meta_description": "Your Stream English profile and course progress",
            "meta_title": "My Profile - Stream English",
        }
    )

    return render(request, "profiles/profile.html", context)


@login_required
def edit_profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect("profiles:profile")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {"u_form": u_form, "p_form": p_form}

    return render(request, "profiles/edit_profile.html", context)


@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been successfully deleted.")
        return redirect("pages:home")
    return redirect("profiles:profile")


# Course-related views
@login_required
def enrol_course(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    # Check if email verification is required
    if course.access == "email" and not request.user.profile.email_verified:
        messages.error(request, "Please verify your email to enrol in this course.")
        request.session["next_url"] = request.path
        return redirect("profiles:profile")

    if request.method == "POST":
        if course not in request.user.profile.enrolled_courses.all():
            request.user.profile.enrolled_courses.add(course)
            messages.success(
                request, f"You have successfully enrolled in {course.title}"
            )
        else:
            messages.info(request, f"You are already enrolled in {course.title}")
    return redirect("courses:course_detail", course_slug=course_slug)


@login_required
def resume_course(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    profile = request.user.profile
    last_watched_lesson = profile.last_watched_lesson

    if last_watched_lesson and last_watched_lesson.course == course:
        return redirect(
            "courses:lesson_detail",
            course_slug=course.slug,
            lesson_slug=last_watched_lesson.slug,
        )
    else:
        first_lesson = course.lesson_set.first()
        if first_lesson:
            return redirect(
                "courses:lesson_detail",
                course_slug=course.slug,
                lesson_slug=first_lesson.slug,
            )
        else:
            messages.warning(request, f"No lessons available in {course.title}")
            return redirect("profiles:profile")


@login_required
def remove_course(request, course_slug):
    if request.method == "POST":
        course = get_object_or_404(Course, slug=course_slug)
        if course in request.user.profile.enrolled_courses.all():
            request.user.profile.enrolled_courses.remove(course)
            messages.success(
                request, f"You have successfully unenrolled from {course.title}"
            )
    return redirect("profiles:profile")

@login_required
@require_http_methods(["POST"])
def mark_video_watched(request, lesson_id):
    try:
        lesson = get_object_or_404(Lesson, id=lesson_id)
        profile = request.user.profile
        
        # Get or create video progress
        progress, created = VideoProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson
        )
        
        # Get current time from request
        data = json.loads(request.body)
        current_time = data.get('current_time', 0)
        
        # Update progress
        progress.current_time = current_time
        progress.is_completed = True
        progress.save()
        
        # Add to watched videos if not already there
        if lesson not in profile.watched_videos.all():
            profile.watched_videos.add(lesson)
            profile.last_watched_lesson = lesson
            profile.save()
            
        return JsonResponse({
            'status': 'success',
            'watched_count': profile.get_watched_videos_count(),
            'course_progress': profile.get_course_completion_percentage(lesson.course)
        })
    except Exception as e:
        logger.error(f"Error marking video as watched: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# Email activation views
def send_activation_email(request, user):
    from django.core.mail import get_connection
    import time
    
    current_site = get_current_site(request)
    unsubscribe_uid = urlsafe_base64_encode(force_bytes(user.pk))
    context = {
        "user": user,
        "domain": current_site.domain,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": account_activation_token.make_token(user),
        "protocol": "https" if request.is_secure() else "http",
        "expiration_days": settings.ACCOUNT_ACTIVATION_DAYS,
        "email": user.email,
        "unsubscribe_url": f"{request.scheme}://{current_site.domain}{reverse('profiles:unsubscribe_email', kwargs={'uidb64': unsubscribe_uid})}",
    }

    html_content = render_to_string("account/email/account_activation_email.html", context)
    text_content = render_to_string("account/email/account_activation_email.txt", context)

    subject = "Activate your Stream English account"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    # Create email message
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")

    # Attempt to send with retries
    for attempt in range(settings.EMAIL_MAX_RETRIES):
        try:
            # Get a fresh connection for each attempt
            connection = get_connection(fail_silently=False)
            connection.open()
            
            # Send email
            msg.connection = connection
            msg.send()
            
            # Log success
            logger.info(f"Successfully sent activation email to {to_email} on attempt {attempt + 1}")
            return True
            
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < settings.EMAIL_MAX_RETRIES - 1:
                time.sleep(settings.EMAIL_RETRY_DELAY)
                continue
            raise  # Re-raise the last exception if all retries failed
        
        finally:
            connection.close()

            
# Activate account
def activate(request, uidb64, token):
    logger.info(f"[Token Debug] Received activation request with token: {token}")
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        logger.info(f"[Token Debug] Found user: {user.username}")
        
        # Add debug token verification
        verification_token = account_activation_token.make_token(user)
        logger.info(f"[Token Debug] Generated verification token: {verification_token}")
        logger.info(f"[Token Debug] Tokens match: {token == verification_token}")

        if user is not None and account_activation_token.check_token(user, token):
            if not user.profile.email_verified:
                user.profile.email_verified = True
                user.profile.save()
                login(request, user)

                try:
                    # Send welcome email after successful activation
                    send_welcome_activated_email(request, user)

                    # Send admin notification
                    send_admin_notification(
                        "New Member Validation",
                        f"New member {user.username} has validated their email address at {timezone.now()}"
                    )
                except Exception as e:
                    logger.error(f"Error sending welcome/notification emails: {str(e)}")
                    
                messages.success(request, "Your account has been successfully activated!")
                return redirect("profiles:profile")
            else:
                messages.info(request, "This account is already activated.")
                return redirect("profiles:login")
        else:
            messages.error(request, "Activation link is invalid or has expired.")
            return redirect("profiles:activation_failed")
            
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        logger.error(f"[Token Debug] Activation error: {str(e)}")
        messages.error(request, "Activation link is invalid.")
        return redirect("profiles:activation_failed")


# Resend activation email
def resend_activation_email(request, uidb64):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and not user.profile.email_verified:
        send_activation_email(request, user)
        messages.success(
            request, "Activation email has been resent. Please check your email."
        )
        return redirect("profiles:login")
    else:
        messages.error(request, "Invalid activation link or user is already active.")
        return redirect("profiles:login")


def extend_activation_time(request, uidb64):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and not user.profile.email_verified:
        extension_days = 7
        user.date_joined = timezone.now()
        user.save()

        send_activation_email(request, user)

        messages.success(
            request,
            f"Your activation period has been extended by {extension_days} days. A new activation email has been sent.",
        )
        return redirect("profiles:login")
    else:
        messages.error(request, "Invalid activation link or email already verified.")
        return redirect("profiles:login")


# Contact views
@login_required
def contact_tutor(request):
    if request.method == "POST":
        if not request.user.profile.email_verified:
            messages.error(request, "Please verify your email to contact the tutor.")
            return redirect("profiles:profile")

        form = ContactForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.save()

            # Email content
            subject = f"New Contact Form Submission: {submission.get_reason_display()}"
            message = f"From: {request.user.username}\n"
            if submission.name:
                message += f"Name: {submission.name}\n"
            message += f"\nDescription: {submission.description}\n"

            if submission.reason == "tuition":
                message += f"\nParent Details:\n"
                message += f"Name: {submission.parent_first_name} {submission.parent_last_name}\n"
                message += f"Email: {submission.parent_email}\n"
                message += f"Phone: {submission.parent_phone}\n"

            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.CONTACT_EMAIL],
                    fail_silently=False,
                )

                print(
                    f"Contact form sent to admin at {settings.CONTACT_EMAIL}"
                )  # Debug print
                messages.success(request, "Your message has been sent successfully!")
            except Exception as e:
                print(f"Error sending contact form: {str(e)}")  # Debug print
                messages.error(
                    request,
                    "There was an error sending your message. Please try again later.",
                )

            return redirect("profiles:profile")

        messages.error(request, "Please correct the errors below.")
    return redirect("profiles:profile")


def unsubscribe_email(request, uidb64):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        # Set user preference to not receive emails
        user.profile.email_subscribed = False
        user.profile.save()

        messages.success(
            request, "You have been successfully unsubscribed from our emails."
        )
        return redirect("pages:home")
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "Invalid unsubscribe link.")
        return redirect("pages:home")


class SecurePasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm

    def form_valid(self, form):
        try:
            check_email_throttle(form.cleaned_data["email"], "password_reset")
        except ValidationError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

        return super().form_valid(form)


def activation_failed(request):
    # Get uidb64 from the request's GET parameters
    uidb64 = request.GET.get("uidb64")
    return render(request, "profiles/activation_failed.html", {"uidb64": uidb64})


class CustomPasswordResetView(FormView):
    form_class = CustomPasswordResetForm
    template_name = "account/password/password_reset_form.html"

    def form_valid(self, form):
        form.save(self.request)
        return super().form_valid(form)


def send_test_email(to_email):
    try:
        logging.debug(f"Starting test email send to {to_email}")
        logging.debug(f"SMTP Settings:")
        logging.debug(f"Host: {settings.EMAIL_HOST}")
        logging.debug(f"Port: {settings.EMAIL_PORT}")
        logging.debug(f"User: {settings.EMAIL_HOST_USER}")
        logging.debug(f"SSL: {settings.EMAIL_USE_SSL}")

        # Create connection with explicit auth
        connection = get_connection()
        connection.open()

        # Force authentication
        if not connection.connection.has_extn("auth"):
            logging.error("SMTP server does not support authentication")
            return False

        try:
            connection.connection.login(
                settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD
            )
            logging.debug("SMTP authentication successful")
        except Exception as e:
            logging.error(f"SMTP authentication failed: {str(e)}")
            return False

        email = EmailMessage(
            "Test Email",
            "This is a test email.",
            settings.DEFAULT_FROM_EMAIL,
            [to_email],
            connection=connection,
        )

        email.send()
        logging.debug("Test email sent successfully")
        connection.close()
        return True

    except Exception as e:
        logging.error(f"Email error: {str(e)}")
        if hasattr(e, "smtp_code"):
            logging.error(f"SMTP Code: {e.smtp_code}")
        if hasattr(e, "smtp_error"):
            logging.error(f"SMTP Error: {e.smtp_error}")
        return False


def test_email_settings():
    import smtplib
    from django.conf import settings

    try:
        print(f"Attempting to connect to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        print(f"Using username: {settings.EMAIL_HOST_USER}")

        # Create SMTP connection using SSL
        server = smtplib.SMTP_SSL(
            settings.EMAIL_HOST, settings.EMAIL_PORT
        )  # Changed back to SMTP_SSL for port 465
        server.set_debuglevel(1)  # Enable debug output

        print("Connection established, attempting login...")
        # Try to login
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

        print("Login successful, closing connection...")
        # Close the connection
        server.quit()
        return True, "SMTP connection successful"
    except Exception as e:
        error_msg = f"SMTP connection failed: {str(e)}"
        print(error_msg)
        return False, error_msg

@login_required
def get_video_progress(request, lesson_id):
    try:
        progress = VideoProgress.objects.get(
            user=request.user,
            lesson_id=lesson_id
        )
        return JsonResponse({
            'current_time': progress.current_time,
            'is_completed': progress.is_completed
        })
    except VideoProgress.DoesNotExist:
        return JsonResponse({'current_time': 0, 'is_completed': False})