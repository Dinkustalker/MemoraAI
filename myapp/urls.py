from django.urls import path
from . import views
from django.urls import path
from myapp import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('reminders/', views.reminders, name='reminders'),
    path('hospitals/', views.hospitals, name='hospitals'),
    path('ai-assistant/', views.ai_assistant, name='ai_assistant'),
    path('analytics/', views.analytics, name='analytics'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('about/', views.about, name='about'),
    path('prescriptions/', views.prescriptions, name='prescriptions'),
    path("appointments/", views.appointments, name="appointments"),
    path("appointment-details/", views.appointment_details, name="appointment_details"),
    path(
        'nearest-hospitals/',
        views.nearest_hospitals,
        name='nearest_hospitals'
    ),
    path("login/", views.login, name="login"),
]


    