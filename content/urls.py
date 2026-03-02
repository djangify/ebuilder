# content/urls.py

from django.urls import path
from . import views

app_name = "content"

urlpatterns = [
    path(
        "gallery/modal/<int:pk>/",
        views.gallery_image_modal,
        name="gallery_image_modal",
    ),
]
