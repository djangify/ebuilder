# pages/admin.py

from django.contrib import admin
from django.contrib.sites.models import Site
from .models import (
    SiteSettings,
    DashboardSettings,
    Page,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Admin interface for site-wide settings."""

    fieldsets = (
        (
            "Currency",
            {
                "fields": ("currency_code", "currency_symbol"),
            },
        ),
        (
            "Color Theme",
            {
                "fields": (
                    "primary_color",
                    "secondary_color",
                    "accent_color",
                    "link_color",
                    "link_hover_color",
                ),
                "description": "You can change your site's color scheme. Changes apply immediately. Choose from Hex #, RGB and HSL",
            },
        ),
        (
            "Homepage Mode",
            {
                "fields": (
                    "homepage_mode",
                    "show_shop_on_homepage",
                    "show_blog_on_homepage",
                ),
            },
        ),
        (
            "Branding",
            {
                "fields": ("business_name", "logo_image"),
            },
        ),
        (
            "Site Identity",
            {
                "fields": ("site_url", "support_email", "site_author"),
            },
        ),
        (
            "Footer",
            {
                "fields": (
                    "social_1_name",
                    "social_1_url",
                    "social_2_name",
                    "social_2_url",
                    "copyright_text",
                ),
            },
        ),
        (
            "Newsletter",
            {
                "fields": ("newsletter_embed_html",),
                "classes": ("collapse",),
            },
        ),
        (
            "Default SEO",
            {
                "fields": (
                    "default_meta_title",
                    "default_meta_description",
                    "default_meta_keywords",
                    "og_image",
                    "facebook_app_id",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Analytics",
            {
                "fields": (
                    "google_analytics_id",
                    "google_search_console_verification",
                ),
                "description": "Add your Google Analytics ID and Google Search Console verification code.",
            },
        ),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Use color picker for color fields."""
        if db_field.name in [
            "primary_color",
            "secondary_color",
            "accent_color",
            "link_color",
            "link_hover_color",
        ]:
            from django.forms import TextInput

            kwargs["widget"] = TextInput(
                attrs={
                    "type": "color",
                    "style": "height: 50px; width: 100px; cursor: pointer;",
                }
            )
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def has_add_permission(self, request):
        """Only allow one SiteSettings instance."""
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of singleton."""
        return False


@admin.register(DashboardSettings)
class DashboardSettingsAdmin(admin.ModelAdmin):
    """
    Admin configuration for Dashboard and Support section.
    Includes the dashboard announcement bar (moved from HomePageSettings).
    """

    fieldsets = (
        (
            "Dashboard Header",
            {
                "fields": (
                    "welcome_heading",
                    "intro_text",
                    "support_url",
                ),
                "description": "Main dashboard greeting text and support link.",
            },
        ),
        (
            "Dashboard Announcement Bar",
            {
                "fields": ("announcement_bar_text",),
                "description": "Optional message shown at the top of the dashboard for logged-in users.",
            },
        ),
        (
            "Left Box — Get In Touch",
            {
                "fields": (
                    "left_title",
                    "response_time",
                    "support_hours",
                    ("policies_link", "docs_link"),
                ),
                "description": "Information shown in the left box of the Support page.",
            },
        ),
        (
            "Right Box — What I Can Help With",
            {
                "fields": (
                    "help_item_1",
                    "help_item_2",
                    "help_item_3",
                    "help_item_4",
                    "help_item_5",
                ),
                "description": "Five optional help topics displayed in the right support box.",
            },
        ),
    )

    list_display = ("__str__", "announcement_bar_text", "updated")
    readonly_fields = ("updated",)

    def has_add_permission(self, request):
        # Enforce singleton pattern
        if DashboardSettings.objects.exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the singleton
        return False


# Unregister the Sites admin
admin.site.unregister(Site)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "template", "published", "menu_order")
    list_filter = ("template", "published")
    prepopulated_fields = {"slug": ("title",)}
    inlines = []

    fieldsets = (
        (
            None,
            {
                "fields": ("title", "slug", "template", "published", "show_title"),
            },
        ),
        (
            "NAVIGATION",
            {
                "fields": ("show_in_navigation", "show_in_footer", "menu_order"),
            },
        ),
        (
            "SEO",
            {
                "fields": ("meta_title", "meta_description"),
            },
        ),
    )

    class Media:
        css = {"all": ("admin/css/admin_fixes.css",)}
