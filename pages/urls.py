from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("about/", views.about_view, name="about"),
    path("gallery/", views.gallery_view, name="gallery"),
    # Custom pages (moved to root-level slug)
    path("<slug:slug>/", views.detail_view, name="detail"),
    # Gallery modal
    path(
        "gallery/modal/<int:pk>/",
        views.gallery_image_modal,
        name="gallery_image_modal",
    ),
]
