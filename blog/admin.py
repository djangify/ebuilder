from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextareaWidget
from .models import Category, Post
from tinymce.widgets import TinyMCE
from django.utils.html import format_html, format_html_join


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


class PostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(attrs={"cols": 80, "rows": 30}))

    class Meta:
        model = Post
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Keep your existing ad_code setup
        if "ad_code" in self.fields:
            self.fields["ad_code"].widget = AdminTextareaWidget(
                attrs={"rows": 6, "class": "vLargeTextField"}
            )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    exclude = ["introduction"]  # hides the introduction field
    list_display = [
        "title",
        "category",
        "status",
        "is_featured",
        "publish_date",
        "display_thumbnail",
        "has_ad",
    ]
    list_editable = ["is_featured"]
    list_filter = ["status", "category", "is_featured", "created", "publish_date"]
    search_fields = ["title", "content", "meta_title", "meta_description"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "publish_date"
    readonly_fields = ["display_media"]

    # Removed external URL validation (requests dependency)
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    @admin.display(boolean=True, description="Ad")
    def has_ad(self, obj):
        return (
            (obj.ad_type != "none")
            or bool((obj.ad_code or "").strip())
            or bool(obj.ad_image)
            or bool(obj.ad_url)
        )

    def display_thumbnail(self, obj):
        image_url = obj.get_thumbnail_url()
        if image_url:
            return format_html('<img src="{}" width="50" />', image_url)
        return "-"

    display_thumbnail.short_description = "Thumbnail"

    def display_media(self, obj):
        html_parts = []
        image_url = obj.get_image_url()
        youtube_url = obj.get_youtube_embed_url()

        if image_url:
            html_parts.append(
                format_html(
                    '<div class="mb-4"><strong>Image:</strong><br/>'
                    '<img src="{}" width="200" /></div>',
                    image_url,
                )
            )

        if youtube_url:
            html_parts.append(
                format_html(
                    '<div class="mb-4"><strong>YouTube Video:</strong><br/>'
                    '<iframe width="400" height="225" src="{}" frameborder="0" allowfullscreen></iframe></div>',
                    youtube_url,
                )
            )

        return (
            format_html_join("", "{}", ((part,) for part in html_parts))
            if html_parts
            else "-"
        )

    display_media.short_description = "Media Preview"
