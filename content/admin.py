from django.contrib import admin
from .models import ContentContainer
from .models import FAQBlock, FAQItem, ThreeColumnBlock


class ThreeColumnBlockInline(admin.StackedInline):
    model = ThreeColumnBlock
    extra = 0
    ordering = ("order",)


@admin.register(ContentContainer)
class ContentContainerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created", "updated")
    readonly_fields = ("created", "updated")
    inlines = [ThreeColumnBlockInline]


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
