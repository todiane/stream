from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.profile, name='profile'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('resend_activation/<uidb64>/', views.resend_activation_email, name='resend_activation'),
    path('extend_activation/<uidb64>/', views.extend_activation_time, name='extend_activation'),
    
]