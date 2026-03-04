from django.contrib import admin
from django import forms
from pages.widgets import RichTextWidget
from .models import (
    ContentContainer,
    HeroBlock,
    FAQBlock,
    FAQItem,
    ThreeColumnBlock,
    SectionBlock,
    NewsletterBlock,
    SpotlightBlock,
    GalleryBlock,
    GalleryImage,
)


class SectionBlockForm(forms.ModelForm):
    class Meta:
        model = SectionBlock
        fields = "__all__"
        widgets = {
            "body": RichTextWidget(),
        }


class HeroBlockInline(admin.StackedInline):
    model = HeroBlock
    extra = 0
    ordering = ("order",)

    fieldsets = (
        (
            "Main Hero Content",
            {
                "fields": (
                    "title",
                    "subtitle",
                    "body",
                    "image",
                    "video_url",
                    "button_text",
                    "button_link",
                )
            },
        ),
        (
            "Banner (Optional Top Strip)",
            {
                "fields": (
                    "banner_published",
                    "banner_badge_text",
                    "banner_text",
                    "banner_action_text",
                    "banner_action_link",
                ),
                "description": "Top announcement strip shown above the hero title. Layout: Badge (left) → Message (centre) → Link (right).",
            },
        ),
        (
            "Display Settings",
            {
                "fields": (
                    "published",
                    "order",
                )
            },
        ),
    )


class ThreeColumnBlockInline(admin.StackedInline):
    model = ThreeColumnBlock
    extra = 0
    ordering = ("order",)


class SectionBlockInline(admin.StackedInline):
    model = SectionBlock
    form = SectionBlockForm
    extra = 1
    can_delete = True
    ordering = ("order",)

    fieldsets = (
        (
            "Content",
            {
                "fields": (
                    "section_type",
                    "title",
                    "subtitle",
                    "body",
                ),
            },
        ),
        (
            "Media",
            {
                "fields": (
                    "image",
                    "image_position",
                ),
            },
        ),
        (
            "Call To Action",
            {
                "fields": (
                    "button_text",
                    "button_link",
                ),
            },
        ),
        (
            "Display Settings",
            {
                "fields": (
                    "order",
                    "published",
                ),
            },
        ),
    )


class NewsletterBlockInline(admin.StackedInline):
    model = NewsletterBlock
    extra = 0
    ordering = ("order",)

    fieldsets = (
        (
            "Content",
            {
                "fields": (
                    "title",
                    "intro_text",
                ),
            },
        ),
        (
            "Embed Code",
            {
                "fields": ("embed_html",),
                "description": "Paste your email provider's embed form HTML.",
            },
        ),
        (
            "Display Settings",
            {
                "fields": (
                    "order",
                    "published",
                ),
            },
        ),
    )


class SpotlightBlockInline(admin.StackedInline):
    model = SpotlightBlock
    extra = 0
    ordering = ("order",)

    fieldsets = (
        (
            "Content",
            {
                "fields": (
                    "title",
                    "body",
                ),
            },
        ),
        (
            "Media",
            {
                "fields": (
                    "image",
                    "image_position",
                ),
            },
        ),
        (
            "Call To Action",
            {
                "fields": (
                    "button_text",
                    "button_link",
                ),
            },
        ),
        (
            "Display Settings",
            {
                "fields": (
                    "order",
                    "published",
                ),
            },
        ),
    )


class GalleryImageInline(admin.StackedInline):
    model = GalleryImage
    extra = 1
    ordering = ("order",)


class GalleryBlockInline(admin.StackedInline):
    model = GalleryBlock
    extra = 0
    ordering = ("order",)
    show_change_link = True


@admin.register(ContentContainer)
class ContentContainerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created", "updated")
    readonly_fields = ("created", "updated")
    inlines = [
        HeroBlockInline,
        SectionBlockInline,
        ThreeColumnBlockInline,
        NewsletterBlockInline,
        SpotlightBlockInline,
        GalleryBlockInline,
    ]

    class Media:
        css = {"all": ("admin/css/admin_fixes.css",)}


class FAQItemInline(admin.TabularInline):
    model = FAQItem
    extra = 0


@admin.register(FAQBlock)
class FAQBlockAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "container", "order", "published")
    list_filter = ("published",)
    inlines = [FAQItemInline]


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ("question", "faq_block", "order", "published")
    list_filter = ("published",)


class ThreeColumnBlockInline(admin.StackedInline):
    model = ThreeColumnBlock
    extra = 0
    ordering = ("order",)

    fieldsets = (
        (
            "Column 1",
            {
                "fields": (
                    "col_1_title",
                    "col_1_image",
                    "col_1_body",
                ),
            },
        ),
        (
            "Column 2",
            {
                "fields": (
                    "col_2_title",
                    "col_2_image",
                    "col_2_body",
                ),
            },
        ),
        (
            "Column 3",
            {
                "fields": (
                    "col_3_title",
                    "col_3_image",
                    "col_3_body",
                ),
            },
        ),
        (
            "Display Settings",
            {
                "fields": (
                    "order",
                    "published",
                ),
            },
        ),
    )


@admin.register(GalleryBlock)
class GalleryBlockAdmin(admin.ModelAdmin):
    list_display = ("title", "container", "order", "published")
    ordering = ("container", "order")
    list_filter = ("published",)
    inlines = [GalleryImageInline]
