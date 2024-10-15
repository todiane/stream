from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.http import HttpResponse
from .tokens import account_activation_token
from django.conf import settings
from django.utils import timezone
from django.urls import reverse


def signup_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            send_activation_email(request, user)
            return HttpResponse('Please confirm your email address to complete the registration')
    else:
        form = UserRegisterForm()
    return render(request, 'profiles/signup.html', {'form': form})


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
                return redirect('profiles:profile')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request, 'profiles/login.html', {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "Thank you, for visiting Stream English. You are now logged out.") 
    return redirect(reverse('profiles:login'))

@login_required
def profile(request):
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

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'profiles/profile.html', context)

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
        # Assuming you have a date_joined field and want to extend by 7 days
        extension_days = 7
        user.date_joined = timezone.now()
        user.save()
        
        # Resend the activation email with the new expiration date
        send_activation_email(request, user)
        
        messages.success(request, f'Your activation period has been extended by {extension_days} days. A new activation email has been sent.')
        return redirect('profiles:login')
    else:
        messages.error(request, 'Invalid activation link or user is already active.')
        return redirect('profiles:login')

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