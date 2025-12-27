# pages/admin.py

from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import (
    Page,
    PageSection,
    ThreeColumnBlock,
    SiteSettings,
    GalleryImage,
    GalleryBlock,
    HeroBanner,
    Hero,
    DashboardSettings,
    FAQBlock,
    FAQItem,
)
from .widgets import TrixWidget

# === Form Customizations ===


class PageSectionForm(forms.ModelForm):
    class Meta:
        model = PageSection
        fields = "__all__"
        widgets = {
            "body": TrixWidget(),
        }


class ThreeColumnBlockForm(forms.ModelForm):
    class Meta:
        model = ThreeColumnBlock
        fields = "__all__"
        widgets = {
            "col_1_body": TrixWidget(),
            "col_2_body": TrixWidget(),
            "col_3_body": TrixWidget(),
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

    fieldsets = (
        (
            "Page Section",
            {
                "fields": (
                    "section_type",
                    "title",
                    "subtitle",
                    "body",
                    "image",
                    "button_text",
                    "button_link",
                    "order",
                    "published",
                )
            },
        ),
    )


class ThreeColumnInline(admin.StackedInline):
    model = ThreeColumnBlock
    form = ThreeColumnBlockForm
    extra = 0
    can_delete = True

    fieldsets = (
        (
            "3-Column Block",
            {
                "fields": (
                    "published",
                    "order",
                    ("col_1_title", "col_1_image"),
                    "col_1_body",
                    ("col_2_title", "col_2_image"),
                    "col_2_body",
                    ("col_3_title", "col_3_image"),
                    "col_3_body",
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


class FAQItemInline(admin.TabularInline):
    model = FAQItem
    extra = 1
    fields = ("question", "answer", "order", "published")
    ordering = ("order",)


class FAQBlockInline(admin.StackedInline):
    model = FAQBlock
    extra = 0
    can_delete = True
    ordering = ("order",)
    fields = ("title", "order", "published")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Site Identity",
            {
                "fields": (
                    "business_name",
                    "site_url",
                    "support_email",
                    "site_author",
                    "logo_image",
                ),
                "description": "Core site information used throughout templates and emails.",
            },
        ),
        (
            "Homepage Mode",
            {
                "fields": (
                    "homepage_mode",
                    "show_shop_on_homepage",
                    "show_blog_on_homepage",
                    "show_gallery_on_homepage",
                ),
                "description": "Control what appears on the homepage.",
            },
        ),
        (
            "Footer",
            {
                "fields": (
                    ("social_1_name", "social_1_url"),
                    ("social_2_name", "social_2_url"),
                    "copyright_text",
                ),
                "description": "Footer social links and copyright.",
            },
        ),
        (
            "Default SEO",
            {
                "fields": (
                    "default_meta_title",
                    "default_meta_description",
                ),
                "description": "Default SEO metadata for pages without their own.",
            },
        ),
    )


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "template", "published", "menu_order")
    list_filter = ("template", "published")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [
        HeroInline,
        PageSectionInline,
        ThreeColumnInline,
        GalleryBlockInline,
        FAQBlockInline,
    ]

    fieldsets = (
        (
            None,
            {
                "fields": ("title", "slug", "template", "published"),
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


@admin.register(FAQBlock)
class FAQBlockAdmin(admin.ModelAdmin):
    list_display = ("title", "page", "order", "published")
    list_filter = ("published", "page")
    ordering = ("page", "order")
    readonly_fields = ("page",)
    inlines = [FAQItemInline]

    def has_add_permission(self, request):
        # FAQ blocks should be added via Page admin inline
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
                "fields": ("image",),
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
