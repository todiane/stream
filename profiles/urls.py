# profiles/urls.py
from django.urls import include, path, reverse_lazy
from django.contrib.auth import views as auth_views
from profiles.forms import CustomPasswordResetForm
from . import views

app_name = 'profiles'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('contact-tutor/', views.contact_tutor, name='contact_tutor'),
    path('purchases/', include('shop.urls'), name='purchases'),
    path('enrol/<slug:course_slug>/', views.enrol_course, name='enrol_course'),
    path('resume/<slug:course_slug>/', views.resume_course, name='resume_course'),
    path('mark-video-watched/<int:lesson_id>/', views.mark_video_watched, name='mark_video_watched'),
    path('remove-course/<slug:course_slug>/', views.remove_course, name='remove_course'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('email/unsubscribe/<uidb64>/', views.unsubscribe_email, name='unsubscribe_email'),
    path('activate/<str:uidb64>/<str:token>/', views.activate, name='activate'),
    path('activation-failed/', views.activation_failed, name='activation_failed'),
    path('resend_activation/<uidb64>/', views.resend_activation_email, name='resend_activation'),
    path('extend_activation/<uidb64>/', views.extend_activation_time, name='extend_activation'),
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='account/password/password_reset_form.html',
             email_template_name='account/email/password_reset_email.html',
             subject_template_name='account/email/password_reset_subject.txt',
             form_class=CustomPasswordResetForm,
             success_url=reverse_lazy('profiles:password_reset_done')
         ), 
         name='password_reset'),
         
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='account/password/password_reset_done.html'
         ), 
         name='password_reset_done'),
         
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='account/password/password_reset_confirm.html',
             success_url=reverse_lazy('profiles:password_reset_complete')
         ), 
         
         name='password_reset_confirm'),
         
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='account/password/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
]