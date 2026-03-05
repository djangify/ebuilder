# pages/models.py
from django.db import models
from django.urls import reverse
import os


class SiteSettings(models.Model):
    """
    Singleton model for site-wide settings.
    Combines branding, navigation, footer, and homepage mode controls.
    """

    # === Currency Settings ===
    CURRENCY_CHOICES = [
        ("AUD", "Australian Dollar (A$)"),
        ("CAD", "Canadian Dollar (CA$)"),
        ("EUR", "Euro (€)"),
        ("GBP", "British Pound (£)"),
        ("USD", "US Dollar ($)"),
    ]

    currency_code = models.CharField(
        "Currency Code",
        max_length=3,
        choices=CURRENCY_CHOICES,
        default="GBP",
        help_text="Currency code for Stripe payments (e.g., GBP, USD, EUR)",
    )
    currency_symbol = models.CharField(
        "Currency Symbol",
        max_length=5,
        default="£",
        help_text="Symbol displayed before prices (e.g., £, $, €)",
    )
    # === Color Theme ===
    primary_color = models.CharField(
        "Primary Color",
        max_length=7,
        default="#0f172a",
        help_text="Main brand color (hex format, e.g., #0f172a)",
    )
    secondary_color = models.CharField(
        "Secondary Color",
        max_length=7,
        default="#334155",
        help_text="Secondary brand color (hex format)",
    )
    accent_color = models.CharField(
        "Accent Color",
        max_length=7,
        default="#475569",
        help_text="Accent/highlight color (hex format)",
    )
    link_color = models.CharField(
        "Link Color",
        max_length=7,
        default="#2563eb",
        help_text="Default link color (hex format)",
    )
    link_hover_color = models.CharField(
        "Link Hover Color",
        max_length=7,
        default="#1d4ed8",
        help_text="Link color on hover (hex format)",
    )
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

    # === Navbar / Branding ===
    business_name = models.CharField(
        "Business Name",
        max_length=150,
        default="My eCommerce Site",
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
        blank=True,
        help_text="Auto-detected from this site. Only change if using a custom domain.",
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
    # === Newsletter signup ===
    newsletter_embed_html = models.TextField(
        "Newsletter Signup HTML",
        blank=True,
        help_text="Paste the HTML embed code from your email provider (Mailchimp, Mailerlite, ConvertKit, etc.)",
    )
    # === Default SEO ===
    default_meta_title = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Default meta title for pages without their own.",
    )
    default_meta_description = models.CharField(
        "Default Meta Description",
        max_length=160,
        blank=True,
        default="Welcome to our online store",
        help_text="Default description for pages without their own (max 160 chars)",
    )
    default_meta_keywords = models.CharField(
        "Default Meta Keywords",
        max_length=255,
        blank=True,
        default="online store, digital products",
        help_text="Default keywords for SEO",
    )
    og_image = models.ImageField(
        "Default OG Image",
        upload_to="site/og/",
        blank=True,
        null=True,
        help_text="Default social sharing image (1200x630px recommended)",
    )
    facebook_app_id = models.CharField(
        "Facebook App ID",
        max_length=50,
        blank=True,
        help_text="Optional Facebook App ID for social features",
    )
    # === Analytics ===
    google_analytics_id = models.CharField(
        "Google Analytics GA4 ID",
        max_length=30,
        blank=True,
        default="",
        help_text="Enter your GA4 Measurement ID (e.g. G-XXXXXXXXXX)",
    )
    google_search_console_verification = models.CharField(
        "Google Search Console Verification Code",
        max_length=255,
        blank=True,
        default="",
        help_text="Enter the content value from Google Search Console meta tag verification.",
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

        # Auto-set site_url if empty
        if not self.site_url:
            from django.contrib.sites.models import Site

            current_site = Site.objects.get_current()
            self.site_url = f"https://{current_site.domain}"

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
    show_title = models.BooleanField(
        default=True, help_text="Uncheck to hide this title from the page."
    )
    content_container = models.OneToOneField(
        "content.ContentContainer",
        on_delete=models.CASCADE,
        related_name="page",
    )

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

    def save(self, *args, **kwargs):
        from content.models import ContentContainer

        # If no container yet, create one
        if not self.content_container_id:
            container = ContentContainer.objects.create(name=f"{self.title} Container")
            self.content_container = container

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        if self.template == "home":
            return reverse("pages:home")
        elif self.template == "about":
            return reverse("pages:about")
        else:
            return reverse("pages:detail", kwargs={"slug": self.slug})


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
