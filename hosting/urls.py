"""
Hosting App URL Configuration

Include in your main urls.py:
    path('', include('hosting.urls')),
"""

from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = "hosting"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("signup/success/", views.signup_success, name="signup_success"),
    path("signup/cancelled/", views.signup_cancelled, name="signup-cancelled"),
    # Preview
    path(
        "signup-preview/",
        TemplateView.as_view(template_name="hosting/signup_success.html"),
    ),
]
