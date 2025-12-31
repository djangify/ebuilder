# accounts/adapters.py

from allauth.account.adapter import DefaultAccountAdapter
from pages.models import SiteSettings
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter to:
    1. Save first_name and last_name during registration
    2. Inject site settings into all email templates
    """

    def save_user(self, request, user, form, commit=True):
        """
        Save the user with first_name and last_name from signup form.
        """
        # Let parent save the user first
        user = super().save_user(request, user, form, commit=False)

        # Get names from POST data (allauth doesn't pass custom fields through form)
        if not user.first_name:
            user.first_name = request.POST.get("first_name", "").strip()

        if not user.last_name:
            user.last_name = request.POST.get("last_name", "").strip()

        if commit:
            user.save()
            logger.info(
                f"User registered: {user.email} ({user.first_name} {user.last_name})"
            )

        return user

    def send_mail(self, template_prefix, email, context):
        """
        Override to inject site settings into all email templates.
        This ensures homepage_settings, site_url, support_email etc. are available.
        """
        # Get site settings from database
        try:
            site_settings = SiteSettings.objects.first()
        except Exception:
            site_settings = None

        # Build the extra context
        if site_settings:
            extra_context = {
                # Primary site settings
                "homepage_settings": site_settings,
                "site_settings": site_settings,
                "site_name": site_settings.business_name,
                "site_url": site_settings.site_url,
                "support_email": site_settings.support_email,
                "business_name": site_settings.business_name,
                # Currency (if needed in emails)
                "currency_symbol": site_settings.currency_symbol,
                "currency_code": site_settings.currency_code,
            }
        else:
            # Fallbacks if SiteSettings doesn't exist
            extra_context = {
                "homepage_settings": None,
                "site_settings": None,
                "site_name": "My Store",
                "site_url": getattr(settings, "SITE_URL", "https://example.com"),
                "support_email": getattr(
                    settings, "DEFAULT_FROM_EMAIL", "support@example.com"
                ),
                "business_name": "My Store",
                "currency_symbol": "£",
                "currency_code": "GBP",
            }

        # Add user's first name if user object exists in context
        if "user" in context and context["user"]:
            user = context["user"]
            extra_context["first_name"] = getattr(user, "first_name", "") or ""
            extra_context["user_name"] = (
                user.get_full_name() if hasattr(user, "get_full_name") else ""
            )

        # Merge extra context (don't overwrite existing values)
        for key, value in extra_context.items():
            if key not in context:
                context[key] = value

        # Call parent send_mail with enriched context
        return super().send_mail(template_prefix, email, context)
