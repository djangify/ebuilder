from django.contrib import admin
from django import forms
from pages.widgets import RichTextWidget
from django.utils.html import format_html
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
    LinkHubBlock,
    LinkHubItem,
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


class LinkHubItemInline(admin.TabularInline):
    model = LinkHubItem
    extra = 1
    max_num = 4


@admin.register(LinkHubBlock)
class LinkHubBlockAdmin(admin.ModelAdmin):
    list_display = ("title", "container", "slug", "order", "published")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("order", "published")
    inlines = [LinkHubItemInline]
    readonly_fields = ("public_linkhub_url",)

    fields = (
        "container",
        "title",
        "slug",
        "public_linkhub_url",
        "logo_image",
        "description",
        "video_url",
        "primary_link",
        "order",
        "published",
    )

    def public_linkhub_url(self, obj):
        if not obj.slug:
            return "Save to generate the public URL."

        url = f"/links/{obj.slug}/"

        return format_html(
            """
            
            <div style="padding:12px;border-radius:6px;max-width:600px;margin-top:6px;">
                <strong>Public LinkHub Page</strong><br>
                After clicking 'Save' your LinkHub page is available at:<br><br>
                <a href="{0}" target="_blank">{0}</a><br><br>
                <a href="{0}" target="_blank"
                style="background:#facc15;padding:6px 10px;border-radius:4px;text-decoration:none;color:black;font-weight:bold;">
                View LinkHub Page
                </a>
            </div>
        
            """,
            url,
        )

    public_linkhub_url.short_description = "LinkHub Page URL"


@admin.register(LinkHubItem)
class LinkHubItemAdmin(admin.ModelAdmin):
    list_display = ("title", "block", "order")
    list_editable = ("order",)
