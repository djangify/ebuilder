from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from ebuilder.mixins.youtube import YouTubeVideoMixin


def get_default_category():
    """Get or create the default 'Uncategorized' category."""

    category, _ = Category.objects.get_or_create(
        slug="uncategorized", defaults={"name": "Uncategorized"}
    )
    return category.pk


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:category", kwargs={"slug": self.slug})


class Post(YouTubeVideoMixin, models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
    ]
    AD_TYPE_CHOICES = [
        ("none", "No Advertisement"),
        ("adsense", "Google AdSense"),
        ("banner", "Banner Image"),
    ]
    RESOURCE_TYPES = [
        ("none", "No Resource"),
        ("pdf", "PDF Document"),
    ]

    # Basic fields
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    content = models.TextField("Content")

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=get_default_category,
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    is_featured = models.BooleanField(
        default=False, help_text="Show this post at the top of the listing"
    )

    # Dates
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    publish_date = models.DateTimeField(null=True, blank=True)

    # Media fields
    image = models.ImageField(upload_to="blog/images/", null=True, blank=True)
    external_image_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="External URL for product image (jpg/png only)",
    )
    youtube_url = models.URLField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to="blog/thumbnails/", null=True, blank=True)
    resource_type = models.CharField(
        max_length=20, choices=RESOURCE_TYPES, default="none"
    )
    resource = models.FileField(upload_to="blog/resources/", null=True, blank=True)
    resource_title = models.CharField(
        max_length=200, blank=True, help_text="Name of the downloadable resource"
    )

    # Advertisement fields
    ad_type = models.CharField(max_length=10, choices=AD_TYPE_CHOICES, default="none")
    ad_code = models.TextField(blank=True)
    ad_image = models.ImageField(upload_to="blog/ads/", null=True, blank=True)
    ad_url = models.URLField(blank=True)

    # SEO fields
    meta_title = models.CharField(
        max_length=60, blank=True, help_text="SEO Title (60 characters max)"
    )
    meta_description = models.CharField(
        max_length=160, blank=True, help_text="SEO Description (160 characters max)"
    )
    meta_keywords = models.CharField(
        max_length=255, blank=True, help_text="Comma-separated keywords"
    )

    class Meta:
        ordering = ["-publish_date", "-created"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("blog:detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == "published" and not self.publish_date:
            self.publish_date = timezone.now()
        super().save(*args, **kwargs)

    def get_image_url(self):
        """Get the URL for the main image"""
        if self.external_image_url:
            return self.external_image_url
        if self.image:
            return self.image.url
        return None

    def get_ad_image_url(self):
        """Get the URL for the advertisement image"""
        if self.ad_image:
            return self.ad_image.url
        return None

    def get_thumbnail_url(self):
        """Get the thumbnail URL - falls back to main image if no thumbnail"""
        try:
            return self.thumbnail.url if self.thumbnail else self.get_image_url()
        except Exception:
            return None

    def get_youtube_video_id(self):
        """Extract YouTube video ID from URL"""
        if not self.youtube_url:
            return None
        if "youtu.be" in self.youtube_url:
            return self.youtube_url.split("/")[-1]
        elif "v=" in self.youtube_url:
            return self.youtube_url.split("v=")[1].split("&")[0]
        return None

    def get_youtube_embed_url(self):
        """Get YouTube video embed URL"""
        video_id = self.get_youtube_video_id()
        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"
        return None

    @property
    def get_meta_title(self):
        """Get meta title with fallback logic"""
        return self.meta_title or self.title[:60]

    @property
    def get_meta_description(self):
        """Get meta description with fallback logic"""
        if self.meta_description:
            return self.meta_description

        if self.content:
            from django.utils.html import strip_tags

            clean_content = strip_tags(self.content)
            return clean_content[:160]

        return self.title
