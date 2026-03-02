from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("about/", views.about_view, name="about"),
    # Custom pages (moved to root-level slug)
    path("<slug:slug>/", views.detail_view, name="detail"),
]
