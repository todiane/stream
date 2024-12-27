# profiles/views.py
import email
from email import message
from email.message import EmailMessage
import logging
from django.core.mail import get_connection
import smtplib
from profiles.models import Profile
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
    send_html_email,
    send_welcome_activated_email,
)
from .utils import check_email_throttle
from django.conf import settings
from django.views.generic.edit import FormView

from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .forms import ContactForm
from .forms import CustomPasswordResetForm
from .tokens import account_activation_token
from courses.models import Course, Lesson


logger = logging.getLogger(__name__)


def signup_view(request):
    # Debug logging at the start
    logging.debug("==== Starting signup process ====")
    logging.debug("Email settings check:")
    logging.debug(f"HOST: {settings.EMAIL_HOST}")
    logging.debug(f"PORT: {settings.EMAIL_PORT}")
    logging.debug(f"USER: {settings.EMAIL_HOST_USER}")
    logging.debug(f"TLS: {settings.EMAIL_USE_TLS}")
    logging.debug(f"FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

    # Test email sending
    send_test_email("info@streamenglish.co.uk")

    if request.method == "POST":
        logger.debug("Signup POST request received")
        logger.debug(f"POST data: {request.POST}")

        form = UserRegisterForm(request.POST)
        if form.is_valid():
            logger.debug("Form is valid, attempting to create user")
            try:
                user = form.save(commit=False)
                user.is_active = True
                user.save()
                logger.debug(f"User created: {user.username}")

                # Get or update the profile
                profile, created = Profile.objects.get_or_create(user=user)
                profile.first_name = form.cleaned_data.get("first_name")
                profile.email_verified = False
                profile.save()
                logger.debug("Profile created/updated")
            except Exception as e:
                logger.error(f"Error creating user or profile: {str(e)}")
                messages.error(
                    request,
                    "There was an error creating your account. Please try again.",
                )
                return redirect("profiles:signup")

                # Prepare email content first
                current_site = get_current_site(request)
                subject = "Activate your Stream English Account"
                unsubscribe_uid = urlsafe_base64_encode(force_bytes(user.pk))

                context = {
                    "user": user,
                    "domain": "streamenglish.co.uk",
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                    "protocol": "https",
                    "expiration_days": settings.ACCOUNT_ACTIVATION_DAYS,
                    "email": user.email,
                    "unsubscribe_url": f"https://streamenglish.co.uk{reverse('profiles:unsubscribe_email', kwargs={'uidb64': unsubscribe_uid})}",
                }
                logger.debug(f"Prepared email context for {user.email}")

                # Send activation email
                try:
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

                    logging.debug("Attempting to send activation email...")
                    msg.send()
                    logging.debug("Activation email sent successfully")

                except Exception as e:
                    logging.error(
                        f"Failed to send activation email: {str(e)}", exc_info=True
                    )
                    logging.error(
                        "SMTP Connection details: HOST=%s, PORT=%s, USER=%s",
                        settings.EMAIL_HOST,
                        settings.EMAIL_PORT,
                        settings.EMAIL_HOST_USER,
                    )
                    raise


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
def mark_video_watched(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    profile = request.user.profile
    profile.watched_videos.add(lesson)
    profile.last_watched_lesson = lesson
    profile.save()
    return redirect(
        "courses:lesson_detail", course_slug=lesson.course.slug, lesson_slug=lesson.slug
    )


# Email activation views
def send_activation_email(request, user):
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

    # Render both HTML and plain text versions
    html_content = render_to_string(
        "account/email/account_activation_email.html", context
    )
    text_content = render_to_string(
        "account/email/account_activation_email.txt", context
    )

    # Create email
    subject = "Activate your Stream English account"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    token = account_activation_token.make_token(user)
    print(f"Generated token: {token}")  # Debugging line


# Activate account
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if not user.profile.email_verified:
            user.profile.email_verified = True
            user.profile.save()
            login(request, user)

            # Send welcome email after successful activation
            send_welcome_activated_email(request, user)

            print("About to send admin notification")  # Debug print
            # Send admin notification
            notification_sent = send_admin_notification(
                "New Member Validation",
                f"New member {user.username} has validated their email address at {timezone.now()}",
            )
            print(f"Admin notification sent: {notification_sent}")  # Debug print

            messages.success(request, "Your account has been successfully activated!")
            return redirect("pages:home")


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
