from django.contrib import admin
from .models import InfoPage, Category
from pages.widgets import RichTextWidget
from django import forms


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


class InfoPageAdminForm(forms.ModelForm):
    class Meta:
        model = InfoPage
        fields = "__all__"
        widgets = {
            "content": RichTextWidget(),
        }


@admin.register(InfoPage)
class InfoPageAdmin(admin.ModelAdmin):
    form = InfoPageAdminForm
    list_display = ("title", "page_type", "category", "published", "last_updated")
    list_filter = ("page_type", "category", "published")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("page_type", "category", "title")

    fieldsets = (
        (None, {"fields": ("title", "slug", "page_type", "category", "published")}),
        ("Content", {"fields": ("content",)}),
        ("Meta", {"fields": ("last_updated",)}),
    )
    readonly_fields = ("last_updated",)
