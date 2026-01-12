"""
Hosting App URL Configuration

Include in your main urls.py:
    path('', include('hosting.urls')),
"""

from django.urls import path
from . import views

app_name = "hosting"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("signup/success/", views.signup_success, name="signup_success"),
    path("signup/cancelled/", views.signup_cancelled, name="signup-cancelled"),
]
