from django.contrib import admin
from django import forms
from pages.widgets import RichTextWidget
from .models import (
    ContentContainer,
    FAQBlock,
    FAQItem,
    ThreeColumnBlock,
    SectionBlock,
    NewsletterBlock,
)


class SectionBlockForm(forms.ModelForm):
    class Meta:
        model = SectionBlock
        fields = "__all__"
        widgets = {
            "body": RichTextWidget(),
        }


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
            "Page Section",
            {
                "fields": (
                    "section_type",
                    "title",
                    "subtitle",
                    "body",
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


class NewsletterBlockInline(admin.StackedInline):
    model = NewsletterBlock
    extra = 0
    ordering = ("order",)


@admin.register(ContentContainer)
class ContentContainerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created", "updated")
    readonly_fields = ("created", "updated")
    inlines = [
        SectionBlockInline,
        ThreeColumnBlockInline,
        NewsletterBlockInline,
    ]


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


@admin.register(ThreeColumnBlock)
class ThreeColumnBlockAdmin(admin.ModelAdmin):
    list_display = ("id", "container", "order", "published")
    list_filter = ("published",)
    ordering = ("container", "order")
