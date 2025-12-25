# blog/urls.py

from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("articles/", views.blog_list, name="list"),
    path("category/<slug:slug>/", views.category_list, name="category"),
    path("<slug:slug>/", views.post_detail, name="detail"),
]
