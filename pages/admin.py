# pages/admin.py

from django.contrib import admin
from django import forms
from django.contrib.sites.models import Site
from django.utils.html import format_html
from .models import (
    Page,
    PageSection,
    SiteSettings,
    GalleryImage,
    GalleryBlock,
    HeroBanner,
    Hero,
    DashboardSettings,
)
from pages.widgets import RichTextWidget

# === Form Customizations ===


class PageSectionForm(forms.ModelForm):
    class Meta:
        model = PageSection
        fields = "__all__"
        widgets = {
            "body": RichTextWidget(),
        }


# === Inlines ===
class HeroInline(admin.StackedInline):
    model = Hero
    extra = 0
    can_delete = True
    fieldsets = (
        (
            "Hero Section",
            {
                "fields": (
                    "title",
                    "subtitle",
                    "body",
                    "image",
                    "video_url",
                    "button_text",
                    "button_link",
                    "order",
                    "is_active",
                )
            },
        ),
    )


class PageSectionInline(admin.StackedInline):
    model = PageSection
    form = PageSectionForm
    extra = 1
    can_delete = True
    readonly_fields = ("admin_note",)

    fieldsets = (
        (
            "Page Section",
            {
                "fields": (
                    "section_type",
                    "title",
                    "subtitle",
                    "body",
                    "admin_note",
                    "image",
                    "image_position",
                    "button_text",
                    "button_link",
                    "order",
                    "published",
                ),
            },
        ),
    )


class GalleryBlockInline(admin.StackedInline):
    model = GalleryBlock
    extra = 0
    can_delete = True
    ordering = ("order",)
    fields = ("title", "order", "published")


class GalleryImageInline(admin.StackedInline):
    model = GalleryImage
    extra = 1
    ordering = ("order",)
    fields = ("image", "display_thumbnail", "title", "caption", "published", "order")
    readonly_fields = ("display_thumbnail",)

    def display_thumbnail(self, obj):
        """Display thumbnail preview in admin."""
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="max-height: 60px; max-width: 100px; object-fit: cover; border-radius: 4px;" />',
                obj.thumbnail.url,
            )
        elif obj.image:
            return format_html(
                '<img src="{}" style="max-height: 60px; max-width: 100px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url,
            )
        return "No image"

    display_thumbnail.short_description = "Preview"


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("title", "gallery", "display_thumbnail", "published", "order")
    list_filter = ("published", "gallery")
    list_editable = ("published", "order")
    search_fields = ("title", "caption")
    ordering = ("gallery", "order")
    readonly_fields = ("display_thumbnail", "thumbnail")

    fieldsets = (
        (
            None,
            {
                "fields": ("gallery", "image", "display_thumbnail"),
            },
        ),
        (
            "Details",
            {
                "fields": ("title", "caption"),
            },
        ),
        (
            "Settings",
            {
                "fields": ("published", "order"),
            },
        ),
    )

    def display_thumbnail(self, obj):
        """Display thumbnail preview in admin."""
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="max-height: 150px; max-width: 200px; object-fit: cover; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.thumbnail.url,
            )
        elif obj.image:
            return format_html(
                '<img src="{}" style="max-height: 150px; max-width: 200px; object-fit: cover; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.image.url,
            )
        return "No image uploaded"

    display_thumbnail.short_description = "Thumbnail Preview"


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


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "template", "published", "menu_order")
    list_filter = ("template", "published")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [
        HeroInline,
        PageSectionInline,
        GalleryBlockInline,
    ]

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


@admin.register(GalleryBlock)
class GalleryBlockAdmin(admin.ModelAdmin):
    list_display = ("title", "page", "order", "published")
    list_filter = ("page", "published")
    ordering = ("page", "order")
    readonly_fields = ("page",)
    inlines = [GalleryImageInline]

    def has_add_permission(self, request):
        # Gallery blocks should be added via Page admin inline
        return False

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["show_save_and_add_another"] = False
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )


@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin):
    """Admin for hero sections."""

    list_display = ("title", "page", "is_active", "order")
    list_filter = ("is_active", "page")
    list_editable = ("is_active", "order")
    ordering = ("page", "order")

    fieldsets = (
        (
            None,
            {
                "fields": ("page", "title", "subtitle", "body", "is_active", "order"),
            },
        ),
        (
            "Media",
            {
                "fields": ("video_url", "image"),
                "description": "Video takes priority if both are provided. Leave both empty for text-only hero.",
            },
        ),
        (
            "Call to Action",
            {
                "fields": ("button_text", "button_link"),
            },
        ),
    )


@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    """Admin for the hero announcement pill/badge."""

    list_display = ("text", "badge_text", "is_active")
    list_editable = ("is_active",)

    fieldsets = (
        (
            None,
            {
                "fields": ("text", "badge_text", "is_active"),
            },
        ),
        (
            "Link",
            {
                "fields": ("action_text", "action_link"),
            },
        ),
    )


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
