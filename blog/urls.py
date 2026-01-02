# blog/urls.py

from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.blog_list, name="list"),
    path("category/", views.category_hub, name="category_hub"),
    path("category/<slug:slug>/", views.category_list, name="category"),
    path("<slug:slug>/", views.post_detail, name="detail"),
]
