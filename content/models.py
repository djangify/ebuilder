from django.db import models
from PIL import Image as PILImage
import os
from io import BytesIO
from django.core.files.base import ContentFile


class ContentContainer(models.Model):
    name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# ============================================
# HERO AND HERO BANNER BLOCK
# ============================================


class HeroBlock(models.Model):
    """
    Unified Hero block attached to ContentContainer.
    Supports video, compression, banner, ordering and publishing.
    """

    container = models.ForeignKey(
        "ContentContainer",
        on_delete=models.CASCADE,
        related_name="hero_blocks",
    )

    # ==============================
    # Main Hero Content
    # ==============================

    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    body = models.TextField(blank=True, null=True)

    image = models.ImageField(
        upload_to="pages/hero/",
        blank=True,
        null=True,
        help_text="Side or background image for the hero section.",
    )

    video_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="YouTube embed URL (takes priority over image)",
    )

    button_text = models.CharField(max_length=100, blank=True)
    button_link = models.URLField(blank=True)

    # ==============================
    # Banner (Integrated)
    # ==============================

    banner_published = models.BooleanField(
        default=False,
        help_text="Enable banner above hero title.",
    )

    # LEFT SIDE — Badge
    banner_badge_text = models.CharField(
        max_length=50,
        blank=True,
        help_text="Small label shown on the left of the banner (e.g. 'New', 'Update', 'Featured').",
    )

    # MIDDLE — Main banner message
    banner_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Main banner message displayed in the centre of the banner.",
    )

    # RIGHT — Link label
    banner_action_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Clickable link text displayed on the right (e.g. 'Read More').",
    )

    # RIGHT — Link URL
    banner_action_link = models.URLField(
        blank=True,
        help_text="URL the banner link should go to. Required if link text is provided.",
    )

    # ==============================
    # Status & Ordering
    # ==============================

    published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title or f"HeroBlock #{self.pk}"

    # ==============================
    # Save Override (Compression)
    # ==============================

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            self._compress_image()

    # ==============================
    # Video Helpers
    # ==============================

    def get_youtube_video_id(self):
        if not self.video_url:
            return None

        url = self.video_url.strip()

        if "youtu.be" in url:
            return url.split("/")[-1].split("?")[0]
        elif "youtube.com/watch?v=" in url:
            return url.split("v=")[1].split("&")[0]
        elif "youtube.com/embed/" in url:
            return url.split("/embed/")[1].split("?")[0]

        return None

    def get_youtube_embed_url(self):
        video_id = self.get_youtube_video_id()
        if video_id:
            return (
                f"https://www.youtube-nocookie.com/embed/"
                f"{video_id}?rel=0&modestbranding=1"
            )
        return None

    # ==============================
    # Image Compression
    # ==============================

    def _compress_image(self):
        try:
            img = PILImage.open(self.image.path)

            import os

            if os.path.getsize(self.image.path) < 50 * 1024:
                return

            if img.mode in ("RGBA", "P"):
                background = PILImage.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(
                    img, mask=img.split()[-1] if img.mode == "RGBA" else None
                )
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            max_width = 1920
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), PILImage.Resampling.LANCZOS)

            webp_path = os.path.splitext(self.image.path)[0] + ".webp"
            img.save(webp_path, "WEBP", quality=75, method=6)

            old_path = self.image.path
            if old_path != webp_path and os.path.exists(old_path):
                os.remove(old_path)

            new_name = os.path.splitext(self.image.name)[0] + ".webp"
            self.__class__.objects.filter(pk=self.pk).update(image=new_name)

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(f"Could not compress Hero image {self.pk}: {e}")


# ============================================
# UNIFIED FAQ BLOCKS
# ============================================


class FAQBlock(models.Model):
    container = models.ForeignKey(
        "content.ContentContainer",
        on_delete=models.CASCADE,
        related_name="faq_blocks",
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional section title like 'Frequently Asked Questions'",
    )
    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "FAQ Block"
        verbose_name_plural = "FAQ Blocks"

    def __str__(self):
        return self.title or f"FAQ Block #{self.pk}"


class FAQItem(models.Model):
    faq_block = models.ForeignKey(
        FAQBlock,
        on_delete=models.CASCADE,
        related_name="items",
    )
    question = models.CharField(max_length=500)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "FAQ Item"
        verbose_name_plural = "FAQ Items"

    def __str__(self):
        return self.question[:50]


class ThreeColumnBlock(models.Model):
    container = models.ForeignKey(
        "ContentContainer",
        on_delete=models.CASCADE,
        related_name="three_column_blocks",
    )

    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    col_1_title = models.CharField(max_length=255, blank=True)
    col_1_image = models.ImageField(upload_to="three_columns/", blank=True, null=True)
    col_1_body = models.TextField(blank=True)

    col_2_title = models.CharField(max_length=255, blank=True)
    col_2_image = models.ImageField(upload_to="three_columns/", blank=True, null=True)
    col_2_body = models.TextField(blank=True)

    col_3_title = models.CharField(max_length=255, blank=True)
    col_3_image = models.ImageField(upload_to="three_columns/", blank=True, null=True)
    col_3_body = models.TextField(blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"ThreeColumnBlock #{self.pk}"


class SectionBlock(models.Model):
    container = models.ForeignKey(
        "ContentContainer",
        on_delete=models.CASCADE,
        related_name="sections",
    )

    SECTION_TYPES = [
        ("text", "Text Block"),
        ("two_column", "Two Column"),
        ("features", "Features Grid"),
        ("cta", "Call to Action"),
    ]

    section_type = models.CharField(max_length=50, choices=SECTION_TYPES)

    title = models.CharField(max_length=200, blank=True)
    subtitle = models.CharField(max_length=300, blank=True)

    body = models.TextField(blank=True, null=True)

    image = models.ImageField(
        upload_to="sections/",
        blank=True,
        null=True,
    )

    IMAGE_POSITION_CHOICES = [
        ("left", "Image Left, Text Right"),
        ("right", "Image Right, Text Left"),
    ]

    image_position = models.CharField(
        max_length=10,
        choices=IMAGE_POSITION_CHOICES,
        default="left",
    )

    button_text = models.CharField(max_length=100, blank=True)
    button_link = models.URLField(blank=True)

    # Two-column fields
    col_1_body = models.TextField(blank=True, null=True)
    col_2_body = models.TextField(blank=True, null=True)

    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"SectionBlock #{self.pk}"


class NewsletterBlock(models.Model):
    container = models.ForeignKey(
        "ContentContainer",
        on_delete=models.CASCADE,
        related_name="newsletter_blocks",
    )

    title = models.CharField(max_length=200, blank=True)
    intro_text = models.TextField(blank=True)

    embed_html = models.TextField(
        help_text="Paste your email provider embed HTML here."
    )

    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title or f"NewsletterBlock #{self.pk}"


class SpotlightBlock(models.Model):
    container = models.ForeignKey(
        "ContentContainer",
        on_delete=models.CASCADE,
        related_name="spotlight_blocks",
    )

    title = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True)

    image = models.ImageField(upload_to="spotlight/", blank=True, null=True)

    image_position = models.CharField(
        max_length=10,
        choices=[("left", "Left"), ("right", "Right")],
        default="right",
    )

    button_text = models.CharField(max_length=255, blank=True)
    button_link = models.URLField(blank=True)

    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title or f"Spotlight #{self.pk}"


class GalleryBlock(models.Model):
    container = models.ForeignKey(
        "ContentContainer",
        on_delete=models.CASCADE,
        related_name="gallery_blocks",
    )

    title = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Gallery Block"
        verbose_name_plural = "Gallery Blocks"

    def __str__(self):
        return self.title or f"GalleryBlock #{self.pk}"


class GalleryImage(models.Model):
    gallery = models.ForeignKey(
        GalleryBlock,
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(upload_to="gallery/")
    thumbnail = models.ImageField(
        upload_to="gallery/thumbnails/",
        blank=True,
        null=True,
        editable=False,
    )

    title = models.CharField(max_length=200, blank=True)
    caption = models.TextField(blank=True)
    published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    THUMBNAIL_SIZE = (300, 300)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title or f"Gallery Image {self.pk}"

    @property
    def alt_text(self):
        return self.title or ""

    def save(self, *args, **kwargs):
        generate_thumbnail = False

        if self.pk:
            try:
                old_instance = GalleryImage.objects.get(pk=self.pk)
                if old_instance.image != self.image:
                    generate_thumbnail = True
                    if old_instance.thumbnail:
                        old_instance.thumbnail.delete(save=False)
            except GalleryImage.DoesNotExist:
                generate_thumbnail = True
        else:
            generate_thumbnail = True

        super().save(*args, **kwargs)

        if generate_thumbnail and self.image:
            self._generate_thumbnail()

    def _generate_thumbnail(self):
        try:
            img = PILImage.open(self.image)

            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            img.thumbnail(self.THUMBNAIL_SIZE, PILImage.Resampling.LANCZOS)

            thumb_io = BytesIO()
            img.save(thumb_io, format="JPEG", quality=85)
            thumb_io.seek(0)

            base_name = os.path.splitext(os.path.basename(self.image.name))[0]
            thumb_filename = f"{base_name}_thumb.jpg"

            self.thumbnail.save(
                thumb_filename,
                ContentFile(thumb_io.read()),
                save=False,
            )

            self.__class__.objects.filter(pk=self.pk).update(
                thumbnail=self.thumbnail.name
            )

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(
                f"Failed to generate thumbnail for GalleryImage {self.pk}: {e}"
            )

    def delete(self, *args, **kwargs):
        image_file = self.image
        thumbnail_file = self.thumbnail

        super().delete(*args, **kwargs)

        if image_file:
            image_file.delete(save=False)
        if thumbnail_file:
            thumbnail_file.delete(save=False)

    def get_thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        if self.image:
            return self.image.url
        return None
