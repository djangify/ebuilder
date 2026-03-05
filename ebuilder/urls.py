# ebuilder/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from ebuilder.sitemaps import sitemaps
from ebuilder import views as project_views
from pages.views_upload import tinymce_upload

urlpatterns = [
    path("health/", project_views.health, name="health"),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("accounts/", include("accounts.urls")),
    path("blog/", include("blog.urls")),
    path("shop/", include("shop.urls")),
    path("tinymce/", include("tinymce.urls")),
    path("tinymce/upload/", tinymce_upload, name="tinymce_upload"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    # Robots.txt
    path("robots.txt", project_views.robots_txt, name="robots_txt"),
    path("", include("hosting.urls")),
    path("", include("infopages.urls")),
    path("", include("content.urls")),
    path("", include("pages.urls")),  # Pages app catch-all must be last
]

# Error handlers
handler404 = "ebuilder.views.handler404"
handler403 = "ebuilder.views.handler403"
handler500 = "ebuilder.views.handler500"

# Static/Media in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin customization
admin.site.site_header = "Djangify eBuilder"
admin.site.site_title = "Djangify eBuilder"
admin.site.index_title = "Welcome to Your Site"
