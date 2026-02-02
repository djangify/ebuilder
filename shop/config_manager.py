# shop/config_manager.py
"""
Configuration manager for eBuilder.
Checks database (ShopSettings) first, falls back to environment variables.
"""

import os
import logging
from typing import Any

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Cache key for config
CONFIG_CACHE_KEY = "ebuilder_config"
CONFIG_CACHE_TIMEOUT = 300  # 5 minutes


class ConfigManager:
    """
    Centralized configuration manager.
    Priority: Database (ShopSettings) > Environment Variables > Defaults
    """

    # Default values for all configurable settings
    DEFAULTS = {
        # Stripe
        "stripe_public_key": "",
        "stripe_secret_key": "",
        "stripe_webhook_secret": "",
        "stripe_live_mode": False,
        # Email
        "email_host": "",
        "email_port": 587,
        "email_use_tls": True,
        "email_host_user": "",
        "email_host_password": "",
        "email_from_address": "",
    }

    # Mapping from config key to environment variable
    ENV_MAPPING = {
        "stripe_public_key": "STRIPE_PUBLIC_KEY",
        "stripe_secret_key": "STRIPE_SECRET_KEY",
        "stripe_webhook_secret": "STRIPE_WEBHOOK_SECRET",
        "stripe_live_mode": "STRIPE_LIVE_MODE",
        "email_host": "EMAIL_HOST",
        "email_port": "EMAIL_PORT",
        "email_use_tls": "EMAIL_USE_TLS",
        "email_host_user": "EMAIL_HOST_USER",
        "email_host_password": "EMAIL_HOST_PASSWORD",
        "email_from_address": "DEFAULT_FROM_EMAIL",
    }

    @classmethod
    def _get_db_settings(cls):
        """Get ShopSettings instance, with caching."""
        from shop.models import ShopSettings

        try:
            return ShopSettings.objects.first()
        except Exception as e:
            logger.debug(f"Could not fetch ShopSettings: {e}")
            return None

    @classmethod
    def _get_from_env(cls, key: str, default: Any = None) -> Any:
        """Get value from environment variable."""
        env_key = cls.ENV_MAPPING.get(key)
        if not env_key:
            return default

        value = os.environ.get(env_key)
        if value is None:
            # Also check Django settings
            value = getattr(settings, env_key, None)

        if value is None:
            return default

        # Type coercion for booleans and integers
        expected_type = type(cls.DEFAULTS.get(key, ""))
        if expected_type is bool:
            return str(value).lower() in ("true", "1", "yes")
        elif expected_type is int:
            try:
                return int(value)
            except (ValueError, TypeError):
                return default

        return value

    @classmethod
    def get(cls, key: str, use_cache: bool = True) -> Any:
        """
        Get configuration value.
        Priority: Database > Environment > Default

        Args:
            key: Configuration key (e.g., 'stripe_secret_key')
            use_cache: Whether to use cached values

        Returns:
            Configuration value
        """
        default = cls.DEFAULTS.get(key)

        # Try database first
        db_settings = cls._get_db_settings()
        if db_settings:
            # Check if the field exists and has a value
            db_value = getattr(db_settings, key, None)
            if db_value not in (None, ""):
                return db_value

        # Fall back to environment
        env_value = cls._get_from_env(key, default)
        return env_value

    @classmethod
    def get_stripe_config(cls):
        """
        Returns Stripe configuration from database or .env.
        Returns None if in demo mode (regardless of keys) or if no keys configured.
        """
        from shop.models import ShopSettings

        try:
            shop_settings = ShopSettings.objects.first()

            # CRITICAL: If demo mode is ON, ALWAYS block payments (even if keys exist)
            if shop_settings and shop_settings.is_demo_site:
                return None

            # Not in demo mode, proceed with normal config
            public_key = (
                shop_settings.stripe_public_key
                if shop_settings and shop_settings.stripe_public_key
                else os.getenv("STRIPE_PUBLIC_KEY", "")
            )
            secret_key = (
                shop_settings.stripe_secret_key
                if shop_settings and shop_settings.stripe_secret_key
                else os.getenv("STRIPE_SECRET_KEY", "")
            )
            webhook_secret = (
                shop_settings.stripe_webhook_secret
                if shop_settings and shop_settings.stripe_webhook_secret
                else os.getenv("STRIPE_WEBHOOK_SECRET", "")
            )

            # Return None if no credentials available
            if not public_key or not secret_key:
                return None

            return {
                "public_key": public_key,
                "secret_key": secret_key,
                "webhook_secret": webhook_secret,
            }
        except Exception:
            # Fallback to .env if database unavailable
            public_key = os.getenv("STRIPE_PUBLIC_KEY", "")
            secret_key = os.getenv("STRIPE_SECRET_KEY", "")

            if not public_key or not secret_key:
                return None

            return {
                "public_key": public_key,
                "secret_key": secret_key,
                "webhook_secret": os.getenv("STRIPE_WEBHOOK_SECRET", ""),
            }

    @classmethod
    def get_email_config(cls) -> dict:
        """Get all email configuration."""
        return {
            "host": cls.get("email_host"),
            "port": cls.get("email_port"),
            "use_tls": cls.get("email_use_tls"),
            "username": cls.get("email_host_user"),
            "password": cls.get("email_host_password"),
            "from_address": cls.get("email_from_address"),
        }

    @classmethod
    def is_stripe_configured(cls) -> bool:
        """Check if Stripe is properly configured."""
        config = cls.get_stripe_config()
        return bool(config["public_key"] and config["secret_key"])

    @classmethod
    def is_email_configured(cls) -> bool:
        """Check if email is properly configured."""
        config = cls.get_email_config()
        return bool(config["host"] and config["username"])

    @classmethod
    def clear_cache(cls):
        """Clear configuration cache."""
        cache.delete(CONFIG_CACHE_KEY)


# Convenience function
def get_config(key: str) -> Any:
    """Shortcut for ConfigManager.get()"""
    return ConfigManager.get(key)
