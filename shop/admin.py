# shop/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.contrib.admin.widgets import AdminSplitDateTime
import requests
from pages.models import SiteSettings

from .models import (
    Category,
    Product,
    ProductDownload,
    ProductImage,
    Order,
    OrderItem,
    ProductReview,
    Purchase,
    ShopPromoBlock,
    ShopSettings,
)
from django import forms

from pages.widgets import RichTextWidget


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "description"]


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 3  # Limits total images to 3
    fields = ["image", "alt_text", "order"]
    ordering = ["order"]


class ProductDownloadInline(admin.TabularInline):
    model = ProductDownload
    extra = 1
    fields = ["label", "file", "order"]
    ordering = ["order"]


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            "description": RichTextWidget(),
            "long_description": RichTextWidget(),
        }


class ShopPromoBlockForm(forms.ModelForm):
    class Meta:
        model = ShopPromoBlock
        fields = "__all__"
        widgets = {
            "col_1_body": RichTextWidget(),
            "col_2_body": RichTextWidget(),
            "col_3_body": RichTextWidget(),
        }


class ShopSettingsForm(forms.ModelForm):
    # Override encrypted fields to use PasswordInput with proper rendering
    stripe_secret_key = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "class": "vTextField",
                "placeholder": "sk_test_... or sk_live_...",
            }
        ),
        help_text="sk_test_... or sk_live_... (encrypted at rest)",
    )
    stripe_webhook_secret = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "class": "vTextField",
                "placeholder": "whsec_...",
            }
        ),
        help_text="whsec_... (encrypted at rest)",
    )
    email_host_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "class": "vTextField",
                "placeholder": "Enter password",
            }
        ),
        help_text="Your SMTP password or app password (encrypted at rest)",
    )

    class Meta:
        model = ShopSettings
        fields = "__all__"
        widgets = {
            "hero_body": RichTextWidget(),
            "intro_body": RichTextWidget(),
            "spotlight_body": RichTextWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Don't show decrypted values in password fields for security
        # User must re-enter if they want to change
        if self.instance and self.instance.pk:
            for field_name in [
                "stripe_secret_key",
                "stripe_webhook_secret",
                "email_host_password",
            ]:
                if getattr(self.instance, field_name, None):
                    self.fields[field_name].widget.attrs["placeholder"] = (
                        "••••••••••••••••"
                    )

    def save(self, commit=True):
        """
        Preserve existing encrypted field values when form field is empty.
        This prevents updating one field from wiping out the others.
        """
        instance = super().save(commit=False)

        # List of encrypted fields to preserve
        encrypted_fields = [
            "stripe_secret_key",
            "stripe_webhook_secret",
            "email_host_password",
        ]

        # If this is an existing record, preserve empty encrypted fields
        if self.instance and self.instance.pk:
            for field_name in encrypted_fields:
                new_value = self.cleaned_data.get(field_name, "")
                if not new_value:
                    # Keep the existing value from the database
                    # We need to get the raw database value, not the decrypted one
                    from shop.models import ShopSettings

                    try:
                        db_instance = ShopSettings.objects.get(pk=self.instance.pk)
                        existing_value = getattr(db_instance, field_name, "")
                        if existing_value:
                            setattr(instance, field_name, existing_value)
                    except ShopSettings.DoesNotExist:
                        pass

        if commit:
            instance.save()
            self.save_m2m()

        return instance


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = [
        "title",
        "category",
        "status",
        "price",
        "sale_price",
        "purchase_count",
        "featured",
        "display_thumbnail",
        "order",
    ]
    list_filter = ["status", "category", "featured", "created"]
    search_fields = ["title", "description", "public_id"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["public_id", "purchase_count", "display_preview"]
    list_editable = ["order", "featured"]
    inlines = [ProductImageInline, ProductDownloadInline]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "public_id",
                    "layout_mode",
                    "title",
                    "slug",
                    "category",
                    "status",
                    "is_active",
                )
            },
        ),
        (
            "Sales Copy",
            {
                "fields": (
                    "description",
                    "long_description",
                )
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "price_pence",
                    "sale_price_pence",
                )
            },
        ),
        (
            "Media",
            {
                "fields": (
                    "preview_image",
                    "external_image_url",
                    "preview_file",
                    "external_preview_url",
                    "video_url",
                ),
            },
        ),
        (
            "Settings",
            {
                "fields": (
                    "download_limit",
                    "featured",
                    "purchase_count",
                    "order",
                )
            },
        ),
    )

    def get_currency_symbol(self):
        """Get currency symbol from SiteSettings"""
        try:
            settings = SiteSettings.objects.first()
            return settings.currency_symbol if settings else "£"
        except Exception:
            return "£"

    def price(self, obj):
        symbol = self.get_currency_symbol()
        return f"{symbol}{obj.price:.2f}"

    def sale_price(self, obj):
        if obj.sale_price_pence:
            symbol = self.get_currency_symbol()
            return f"{symbol}{obj.sale_price:.2f}"
        return "-"

    def display_thumbnail(self, obj):
        image_url = obj.get_image_url()
        if image_url:
            return format_html(
                '<img src="{}" width="50" class="admin-thumbnail" style="border-radius: 3px;" />',
                image_url,
            )
        return "-"

    display_thumbnail.short_description = "Thumbnail"

    def display_preview(self, obj):
        html = []
        image_url = obj.get_image_url()
        if image_url:
            html.append(
                f'<div class="mb-4"><strong>Preview Image:</strong><br/>'
                f'<img src="{image_url}" width="200" style="border-radius: 5px; '
                f'box-shadow: 0 2px 5px rgba(0,0,0,0.1);" /></div>'
            )
        return format_html("".join(html)) if html else "-"

    display_preview.short_description = "Preview"

    def clean_external_preview_url(self, url):
        if not url:
            return url

        validator = URLValidator()
        try:
            validator(url)
        except ValidationError:
            raise ValidationError("Invalid URL format")

        try:
            response = requests.head(url, allow_redirects=True)
            content_type = response.headers.get("content-type", "").lower()

            if not content_type == "application/pdf":
                raise ValidationError("URL must point to a PDF file")

        except requests.RequestException:
            raise ValidationError("Could not validate preview URL")

        return url

    def save_model(self, request, obj, form, change):
        if "external_image_url" in form.changed_data:
            obj.external_image_url = self.clean_external_image_url(
                obj.external_image_url
            )
        if "external_preview_url" in form.changed_data:
            obj.external_preview_url = self.clean_external_preview_url(
                obj.external_preview_url
            )
        super().save_model(request, obj, form, change)

    def clean_external_image_url(self, url):
        if not url:
            return url

        validator = URLValidator()
        try:
            validator(url)
        except ValidationError:
            raise ValidationError("Invalid URL format")

        try:
            response = requests.head(url, allow_redirects=True)
            content_type = response.headers.get("content-type", "").lower()

            if not content_type.startswith("image/"):
                raise ValidationError("URL must point to an image file")

            if not any(
                content_type.endswith(ext) for ext in ["/jpeg", "/jpg", "/png", "/webp"]
            ):
                raise ValidationError("Only JPG and PNG images are allowed")

        except requests.RequestException:
            raise ValidationError("Could not validate image URL")

        return url


class ShopPromoBlockInline(admin.StackedInline):
    model = ShopPromoBlock
    form = ShopPromoBlockForm
    extra = 0
    can_delete = True
    ordering = ("order",)

    fieldsets = (
        (
            "Block Settings",
            {
                "fields": ("order", "published"),
            },
        ),
        (
            "Column 1",
            {
                "fields": ("col_1_title", "col_1_image", "col_1_body"),
                "classes": ("collapse",),
            },
        ),
        (
            "Column 2",
            {
                "fields": ("col_2_title", "col_2_image", "col_2_body"),
                "classes": ("collapse",),
            },
        ),
        (
            "Column 3",
            {
                "fields": ("col_3_title", "col_3_image", "col_3_body"),
                "classes": ("collapse",),
            },
        ),
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ["product"]
    fields = [
        "product",
        "quantity",
        "price_paid_pence",
        "downloads_remaining",
    ]
    ordering = ["id"]
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_id", "user", "email", "paid", "created", "get_customer_name"]
    list_filter = ["paid", "created", "status"]
    search_fields = [
        "order_id",
        "user__username",
        "email",
    ]
    inlines = [OrderItemInline]
    readonly_fields = ["order_id", "payment_intent_id"]

    def get_customer_name(self, obj):
        if obj.user:
            if obj.user.first_name and obj.user.last_name:
                return f"{obj.user.first_name} {obj.user.last_name}"
            elif obj.user.first_name:
                return obj.user.first_name
            else:
                return obj.user.username

        return "No user assigned"

    get_customer_name.short_description = "Customer"

    fieldsets = (
        (None, {"fields": ("order_id", "user", "email", "status", "paid")}),
        (
            "Payment Information",
            {"fields": ("payment_intent_id",), "classes": ("collapse",)},
        ),
    )


admin.site.register(Purchase)


class ProductReviewAdminForm(forms.ModelForm):
    created_override = forms.SplitDateTimeField(
        label="Created",
        widget=AdminSplitDateTime,
        required=True,
        help_text="Set the review's created date/time.",
    )

    class Meta:
        model = ProductReview
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.created:
            self.fields["created_override"].initial = self.instance.created

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.created = self.cleaned_data["created_override"]
        if commit:
            obj.save()
            self.save_m2m()
        return obj


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    form = ProductReviewAdminForm

    list_display = ["product", "user", "rating", "verified_purchase", "created"]
    list_filter = ["rating", "verified_purchase", "created"]
    search_fields = ["product__title", "user__username", "comment"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "product",
                    "user",
                    "rating",
                    "comment",
                    "created_override",
                    "verified_purchase",
                )
            },
        ),
    )

    readonly_fields = []

    def save_model(self, request, obj, form, change):
        obj.verified_purchase = True
        super().save_model(request, obj, form, change)


@admin.register(ShopSettings)
class ShopSettingsAdmin(admin.ModelAdmin):
    form = ShopSettingsForm
    inlines = [ShopPromoBlockInline]

    fieldsets = (
        (
            "Demo Site Settings",
            {
                "fields": ("is_demo_site",),
                "description": "Enable demo mode for sites being built for sale. Disables payments until Stripe is configured.",
            },
        ),
        (
            "Hero Section",
            {
                "fields": (
                    "hero_title",
                    "hero_subtitle",
                    "hero_body",
                    "hero_image",
                    "hero_button_text",
                    "hero_button_link",
                ),
                "description": "The main banner area at the top of your shop homepage.",
            },
        ),
        (
            "Intro Section",
            {
                "fields": (
                    "show_intro_section",
                    "intro_title",
                    "intro_body",
                ),
                "description": "Optional text block below the hero.",
                "classes": ("collapse",),
            },
        ),
        (
            "Product Spotlight",
            {
                "fields": (
                    "show_spotlight",
                    "spotlight_title",
                    "spotlight_body",
                    "spotlight_image",
                    "spotlight_image_position",
                    "spotlight_button_text",
                    "spotlight_button_link",
                ),
                "description": "Two-column section to highlight a product or promotion.",
                "classes": ("collapse",),
            },
        ),
        (
            "Section Ordering",
            {
                "fields": (
                    "intro_order",
                    "promo_blocks_order",
                    "spotlight_order",
                ),
                "description": "Control the display order of sections. Lower numbers appear first. Hero is always at the top, products always at the bottom.",
            },
        ),
        (
            "Promo Blocks",
            {
                "fields": ("show_promo_blocks",),
                "description": "Toggle the three-column promo blocks. Add blocks using the inline below.",
            },
        ),
        (
            "Display Options",
            {
                "fields": (
                    "show_products_on_homepage",
                    "products_per_page",
                    "product_display_mode",
                    "display_category",
                ),
                "description": "Control which products appear and pagination.",
            },
        ),
        (
            "Stripe Configuration",
            {
                "fields": (
                    "stripe_live_mode",
                    "stripe_public_key",
                    "stripe_secret_key",
                    "stripe_webhook_secret",
                ),
                "description": "Payment gateway settings. Leave blank to use .env values. Secrets are encrypted at rest.",
                "classes": ("collapse",),
            },
        ),
        (
            "Email Configuration",
            {
                "fields": (
                    "email_host",
                    "email_port",
                    "email_use_tls",
                    "email_host_user",
                    "email_host_password",
                    "email_from_address",
                ),
                "description": "SMTP settings for transactional emails. Leave blank to use .env values.",
                "classes": ("collapse",),
            },
        ),
    )

    def has_add_permission(self, request):
        # Only allow one instance
        return not ShopSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        """Add warning banner if Stripe not configured or in demo mode"""
        extra_context = extra_context or {}

        try:
            settings = ShopSettings.objects.first()
            if settings:
                # Check if demo mode
                if settings.is_demo_site:
                    extra_context["demo_mode_warning"] = True

                # Check if Stripe configured
                stripe_configured = bool(
                    settings.stripe_secret_key and settings.stripe_public_key
                )
                if not stripe_configured:
                    extra_context["stripe_not_configured"] = True

        except ShopSettings.DoesNotExist:
            extra_context["stripe_not_configured"] = True

        return super().changelist_view(request, extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """Add warning to change form"""
        extra_context = extra_context or {}

        try:
            settings = ShopSettings.objects.get(pk=object_id)
            if settings.is_demo_site:
                extra_context["demo_mode_warning"] = True

            stripe_configured = bool(
                settings.stripe_secret_key and settings.stripe_public_key
            )
            if not stripe_configured:
                extra_context["stripe_not_configured"] = True

        except ShopSettings.DoesNotExist:
            pass

        return super().change_view(request, object_id, form_url, extra_context)
