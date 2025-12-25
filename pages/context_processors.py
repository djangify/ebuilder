# pages/context_processors.py
from django.contrib.sites.models import Site
from .models import Page, SiteSettings, DashboardSettings
from django.conf import settings


def ebuilder_settings(request):
    """
    Provide site-wide settings to all templates.
    Pulls from SiteSettings model (admin-editable) with sensible fallbacks.
    """
    try:
        site_settings = SiteSettings.objects.first()
    except Exception:
        site_settings = None

    if site_settings:
        return {
            # License key (from .env, not admin)
            "EBUILDER_LICENSE_KEY": getattr(settings, "EBUILDER_LICENSE_KEY", ""),
            # From SiteSettings model (admin-editable)
            "site_url": site_settings.site_url,
            "site_name": site_settings.business_name,
            "support_email": site_settings.support_email,
            "site_author": site_settings.site_author or site_settings.business_name,
        }
    else:
        # Fallbacks if SiteSettings doesn't exist yet
        return {
            "EBUILDER_LICENSE_KEY": getattr(settings, "EBUILDER_LICENSE_KEY", ""),
            "site_url": "https://example.com",
            "site_name": "My Store",
            "support_email": "hello@example.com",
            "site_author": "My Store",
        }


def published_pages(request):
    """Make published pages available for navigation menus."""
    pages = Page.objects.filter(published=True, show_in_navigation=True).order_by(
        "menu_order", "title"
    )

    return {"published_pages": pages}


def site_settings(request):
    """
    Make SiteSettings globally available.
    Replaces the old homepage_settings context processor from core.
    """
    try:
        settings = SiteSettings.objects.first()
        social_links = settings.social_links if settings else []
    except Exception:
        settings = None
        social_links = []

    return {
        "site_settings": settings,
        "social_links": social_links,
        # Backwards compatibility alias
        "homepage_settings": settings,
    }


def home_url(request):
    """
    Provide the correct home URL based on homepage_mode setting.
    """
    from django.urls import reverse

    try:
        settings = SiteSettings.objects.first()
    except Exception:
        settings = None

    if settings and settings.homepage_mode == "PAGES":
        url = reverse("pages:home")
    else:
        # Default to shop
        try:
            url = reverse("shop:product_list")
        except Exception:
            url = "/"

    return {"HOME_URL": url}


def current_site(request):
    """Make the current Site object available in templates."""
    try:
        site = Site.objects.get_current()
    except Site.DoesNotExist:
        site = None
    return {"site": site}


def dashboard_settings(request):
    """
    Makes DashboardSettings data globally available.
    Used by dashboard.html and support.html templates.
    Now includes announcement_bar_text (moved from HomePageSettings).
    """
    try:
        settings = DashboardSettings.objects.first()
    except Exception:
        settings = None
    return {"dashboard_settings": settings}
