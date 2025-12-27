# pages/models.py

from django.db import models
from django.urls import reverse
import os
from io import BytesIO
from PIL import Image as PILImage
from django.core.files.base import ContentFile


class SiteSettings(models.Model):
    """
    Singleton model for site-wide settings.
    Combines branding, navigation, footer, and homepage mode controls.
    """

    # === Homepage Mode ===
    HOMEPAGE_CHOICES = [
        ("SHOP", "Shop Homepage"),
        ("PAGES", "Pages Homepage"),
    ]
    homepage_mode = models.CharField(
        max_length=10,
        choices=HOMEPAGE_CHOICES,
        default="PAGES",
        help_text="Choose whether the shop or pages homepage is displayed at the root URL.",
    )

    # === Homepage Content Toggles ===
    show_shop_on_homepage = models.BooleanField(
        default=False,
        help_text="Show featured products on the homepage.",
    )
    show_blog_on_homepage = models.BooleanField(
        default=False,
        help_text="Show the latest 3 blog posts on the homepage.",
    )
    show_gallery_on_homepage = models.BooleanField(
        default=False,
        help_text="Show gallery images on the homepage.",
    )

    # === Navbar / Branding ===
    business_name = models.CharField(
        "Business Name",
        max_length=150,
        default="My Site",
        help_text="Displayed in the navbar next to the logo.",
    )
    logo_image = models.ImageField(
        "Logo Image",
        upload_to="site/logo/",
        blank=True,
        null=True,
        help_text="Optional logo to display in the navbar beside the business name.",
    )
    # === Site Identity  ===
    site_url = models.URLField(
        "Site URL",
        max_length=200,
        default="https://example.com",
        help_text="Your full site URL including https:// (e.g., https://mystore.com)",
    )
    support_email = models.EmailField(
        "Support Email",
        max_length=254,
        default="hello@example.com",
        help_text="Email address shown in templates for customer support.",
    )
    site_author = models.CharField(
        "Site Author/Owner",
        max_length=150,
        blank=True,
        help_text="Name shown in meta tags and schema markup (e.g., 'Jane Smith' or 'My Company').",
    )

    # === Footer ===
    social_1_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="e.g. LinkedIn",
    )
    social_1_url = models.URLField(blank=True, null=True)
    social_2_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="e.g. Instagram",
    )
    social_2_url = models.URLField(blank=True, null=True)
    copyright_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional custom copyright text. Leave blank to auto-generate.",
    )

    # === Default SEO ===
    default_meta_title = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Default meta title for pages without their own.",
    )
    default_meta_description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Default meta description for pages without their own.",
    )

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"

    def save(self, *args, **kwargs):
        # Enforce singleton
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError("Only one SiteSettings instance is allowed.")
        super().save(*args, **kwargs)

    @property
    def get_copyright(self):
        return self.copyright_text or f"© {self.business_name}. All rights reserved."

    @property
    def social_links(self):
        """Return list of (name, url) tuples for active social links."""
        links = []
        if self.social_1_name and self.social_1_url:
            links.append((self.social_1_name, self.social_1_url))
        if self.social_2_name and self.social_2_url:
            links.append((self.social_2_name, self.social_2_url))
        return links


class Page(models.Model):
    TEMPLATE_CHOICES = [
        ("home", "Homepage"),
        ("about", "About"),
        ("custom", "Custom Page"),
        ("gallery", "Gallery Page"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    template = models.CharField(max_length=20, choices=TEMPLATE_CHOICES)
    published = models.BooleanField(default=True)

    # SEO
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Navigation controls
    show_in_navigation = models.BooleanField(
        default=True,
        help_text="Show this page in the top navigation bar.",
    )
    show_in_footer = models.BooleanField(
        default=True,
        help_text="Show this page in the footer links.",
    )
    menu_order = models.PositiveIntegerField(
        default=0,
        help_text="Control the order of this page in the navigation.",
    )

    class Meta:
        ordering = ["menu_order", "title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.template == "home":
            return reverse("pages:home")
        elif self.template == "about":
            return reverse("pages:about")
        elif self.template == "gallery":
            return reverse("pages:gallery")
        return reverse("pages:detail", kwargs={"slug": self.slug})


class PageSection(models.Model):
    SECTION_TYPES = [
        ("text", "Text Block"),
        ("two_column", "Two Column"),
        ("features", "Features Grid"),
        ("cta", "Call to Action"),
    ]

    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="sections")
    section_type = models.CharField(max_length=50, choices=SECTION_TYPES)
    title = models.CharField(max_length=200, blank=True)
    subtitle = models.CharField(max_length=300, blank=True)
    body = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="pages/sections/", blank=True, null=True)
    button_text = models.CharField(max_length=100, blank=True)
    button_link = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    # Two-column fields
    col_1_body = models.TextField(blank=True, null=True)
    col_2_body = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Page Section"
        verbose_name_plural = "PAGE SECTIONS"

    def __str__(self):
        return f"{self.page.title} - {self.get_section_type_display()}"


class ThreeColumnBlock(models.Model):
    page = models.ForeignKey(
        Page, on_delete=models.CASCADE, related_name="three_columns"
    )
    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    col_1_title = models.CharField(max_length=150, blank=True)
    col_1_image = models.ImageField(upload_to="pages/columns/", blank=True, null=True)
    col_1_body = models.TextField(blank=True, null=True)

    col_2_title = models.CharField(max_length=150, blank=True)
    col_2_image = models.ImageField(upload_to="pages/columns/", blank=True, null=True)
    col_2_body = models.TextField(blank=True, null=True)

    col_3_title = models.CharField(max_length=150, blank=True)
    col_3_image = models.ImageField(upload_to="pages/columns/", blank=True, null=True)
    col_3_body = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Three Column Block"
        verbose_name_plural = "THREE COLUMN BLOCKS"

    def __str__(self):
        return f"{self.page.title} - 3-Column Block"


class GalleryBlock(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="galleries")
    title = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Gallery Block"
        verbose_name_plural = "GALLERY BLOCKS"

    def __str__(self):
        return f"{self.page.title} - Gallery: {self.title or 'Untitled'}"


class GalleryImage(models.Model):
    gallery = models.ForeignKey(
        GalleryBlock,
        on_delete=models.CASCADE,
        related_name="images",
        blank=True,
        null=True,
    )
    image = models.ImageField(upload_to="pages/gallery/")
    thumbnail = models.ImageField(
        upload_to="pages/gallery/thumbnails/",
        blank=True,
        null=True,
        editable=False,  # Auto-generated, not editable in admin
    )
    title = models.CharField(max_length=200, blank=True)
    caption = models.TextField(blank=True)
    published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    # Thumbnail settings
    THUMBNAIL_SIZE = (300, 300)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title or f"Gallery Image {self.pk}"

    @property
    def alt_text(self):
        """Return alt text for templates."""
        return self.title or ""

    def save(self, *args, **kwargs):
        # Track if image has changed
        generate_thumbnail = False

        if self.pk:
            # Existing instance - check if image changed
            try:
                old_instance = GalleryImage.objects.get(pk=self.pk)
                if old_instance.image != self.image:
                    generate_thumbnail = True
                    # Delete old thumbnail if it exists
                    if old_instance.thumbnail:
                        old_instance.thumbnail.delete(save=False)
            except GalleryImage.DoesNotExist:
                generate_thumbnail = True
        else:
            # New instance
            generate_thumbnail = True

        # Save first to ensure we have the image file
        super().save(*args, **kwargs)

        # Generate thumbnail if needed
        if generate_thumbnail and self.image:
            self._generate_thumbnail()

    def _generate_thumbnail(self):
        """Generate a thumbnail from the main image."""
        if not self.image:
            return

        try:
            # Open the image
            img = PILImage.open(self.image)

            # Convert to RGB if necessary (for PNG with transparency, etc.)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Create thumbnail (maintains aspect ratio)
            img.thumbnail(self.THUMBNAIL_SIZE, PILImage.Resampling.LANCZOS)

            # Save to BytesIO
            thumb_io = BytesIO()
            img.save(thumb_io, format="JPEG", quality=85)
            thumb_io.seek(0)

            # Generate thumbnail filename
            base_name = os.path.splitext(os.path.basename(self.image.name))[0]
            thumb_filename = f"{base_name}_thumb.jpg"

            # Save thumbnail without triggering another save()
            self.thumbnail.save(
                thumb_filename,
                ContentFile(thumb_io.read()),
                save=False,
            )

            # Update just the thumbnail field
            GalleryImage.objects.filter(pk=self.pk).update(
                thumbnail=self.thumbnail.name
            )

        except Exception as e:
            # Log error but don't break the save
            import logging

            logger = logging.getLogger(__name__)
            logger.error(
                f"Failed to generate thumbnail for GalleryImage {self.pk}: {e}"
            )

    def delete(self, *args, **kwargs):
        """Delete associated image files when model is deleted."""
        # Store file references before delete
        image_file = self.image
        thumbnail_file = self.thumbnail

        super().delete(*args, **kwargs)

        # Delete files after model delete
        if image_file:
            image_file.delete(save=False)
        if thumbnail_file:
            thumbnail_file.delete(save=False)

    def get_thumbnail_url(self):
        """Return thumbnail URL, falling back to main image if no thumbnail."""
        if self.thumbnail:
            return self.thumbnail.url
        if self.image:
            return self.image.url
        return None


class FAQBlock(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="faqs")
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
        verbose_name_plural = "FAQ BLOCKS"

    def __str__(self):
        return f"{self.page.title} - FAQ: {self.title or 'Untitled'}"


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


class Hero(models.Model):
    """
    Hero section for pages.
    Each hero belongs to a specific page.
    """

    page = models.ForeignKey(
        "Page",
        on_delete=models.CASCADE,
        related_name="heroes",
        null=True,  # Allows existing heroes to migrate without breaking
        blank=True,
        help_text="Select which page this hero belongs to.",
    )
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    body = models.TextField(blank=True, null=True)
    image = models.ImageField(
        upload_to="pages/hero/",
        blank=True,
        null=True,
        help_text="Background image for the hero section.",
    )
    button_text = models.CharField(max_length=100, blank=True)
    button_link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Hero Section"
        verbose_name_plural = "Hero Sections"
        ordering = ["order"]

    def __str__(self):
        page_name = self.page.title if self.page else "Unassigned"
        return f"{page_name} - {self.title}"


class HeroBanner(models.Model):
    """
    Small announcement pill/badge shown above the hero title.
    e.g., "New → Check out our latest products"
    """

    text = models.CharField(max_length=200, default="New Resources Available!")
    action_text = models.CharField(max_length=100, default="See what's new")
    action_link = models.CharField(max_length=200, blank=True)
    badge_text = models.CharField(max_length=50, default="New")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Hero Banner"
        verbose_name_plural = "Hero Banners"

    def __str__(self):
        return self.text


class DashboardSettings(models.Model):
    """
    Controls the text, support details, and help items shown
    on the customer dashboard and support page.
    Singleton pattern – only one instance allowed.
    """

    # === Dashboard Header ===
    welcome_heading = models.CharField(
        max_length=150,
        default="Welcome,",
        help_text="Main heading text at the top of the dashboard.",
    )
    intro_text = models.TextField(
        blank=True,
        null=True,
        default="Here's an overview of your account and quick access to your saved items.",
        help_text="Displayed under the welcome heading on the dashboard.",
    )
    support_url = models.URLField(
        blank=True,
        null=True,
        help_text="Optional custom URL for the support/contact page. Defaults to /support/.",
    )

    # === Dashboard Announcement Bar  ===
    announcement_bar_text = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Optional announcement message shown at the top of the dashboard.",
    )

    # === Left Box: Get In Touch ===
    left_title = models.CharField(
        max_length=100,
        default="Get In Touch",
        help_text="Title for the left box on the support page.",
    )
    response_time = models.CharField(
        max_length=100,
        default="Within 48 hours (weekdays)",
        help_text="Displayed response time.",
    )
    support_hours = models.CharField(
        max_length=100,
        default="Monday – Friday, 9AM – 4PM GMT",
        help_text="Displayed support hours.",
    )
    policies_link = models.URLField(
        blank=True,
        null=True,
        help_text="Optional link to policies index page.",
    )
    docs_link = models.URLField(
        blank=True,
        null=True,
        help_text="Optional link to documentation page.",
    )

    # === Right Box: What I Can Help With ===
    help_item_1 = models.CharField(max_length=150, blank=True, null=True)
    help_item_2 = models.CharField(max_length=150, blank=True, null=True)
    help_item_3 = models.CharField(max_length=150, blank=True, null=True)
    help_item_4 = models.CharField(max_length=150, blank=True, null=True)
    help_item_5 = models.CharField(max_length=150, blank=True, null=True)

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dashboard Settings"
        verbose_name_plural = "Dashboard Settings"

    def __str__(self):
        return "Dashboard & Support Settings"

    def save(self, *args, **kwargs):
        # Enforce singleton
        if not self.pk and DashboardSettings.objects.exists():
            raise ValueError("Only one DashboardSettings instance is allowed.")
        super().save(*args, **kwargs)
