# content/urls.py

from django.urls import path
from . import views
from .views import linkhub_page

app_name = "content"

urlpatterns = [
    path(
        "gallery/modal/<int:pk>/",
        views.gallery_image_modal,
        name="gallery_image_modal",
    ),
    path("links/<slug:slug>/", linkhub_page, name="linkhub_page"),
]
