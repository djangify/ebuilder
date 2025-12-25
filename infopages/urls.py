from django.urls import path
from . import views

app_name = "infopages"

urlpatterns = [
    # Documentation hub and categories
    path("docs/", views.DocListView.as_view(), name="docs_index"),
    path(
        "docs/category/<slug:slug>/",
        views.CategoryDetailView.as_view(),
        name="category_detail",
    ),
    path("docs/<slug:slug>/", views.InfoPageDetailView.as_view(), name="doc_detail"),
    # Policies
    path("policies/", views.PolicyListView.as_view(), name="policy_index"),
    path(
        "policies/<slug:slug>/",
        views.InfoPageDetailView.as_view(),
        name="policy_detail",
    ),
]
