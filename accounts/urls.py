# accounts/urls.py

from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("profile/", views.profile_view, name="profile"),
    path("delete-account/", views.delete_account_view, name="delete_account"),
    path("support/", views.support, name="support"),
]
