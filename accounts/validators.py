# accounts/validators.py
"""
Anti-spam validators for registration:
- Disposable email blocking
- Honeypot trap detection
- Time-based bot detection
"""

import time
import logging
from django.core.exceptions import ValidationError
from disposable_email_domains import blocklist

logger = logging.getLogger(__name__)


def validate_not_disposable_email(email):
    """
    Check if email domain is a known disposable/temporary email service.
    Blocks registration from throwaway email addresses.
    """
    domain = email.split("@")[-1].lower()

    if domain in blocklist:
        logger.warning(f"Blocked disposable email registration attempt: {email}")
        raise ValidationError(
            "Please use a permanent email address. Temporary email services are not allowed."
        )


def validate_honeypot(request):
    """
    Check honeypot field - bots fill it, humans don't see it.
    Returns True if bot detected, False if legitimate.
    """
    honeypot_value = request.POST.get("website_url", "")

    if honeypot_value:
        logger.warning(
            f"Honeypot triggered - bot detected from IP: {get_client_ip(request)}"
        )
        return True
    return False


def validate_form_timing(request, min_seconds=3):
    """
    Check form submission timing - humans take time, bots are instant.
    Returns True if bot detected (too fast), False if legitimate.
    """
    form_timestamp = request.POST.get("form_timestamp", "")

    if not form_timestamp:
        return False  # Field missing, let other validation handle it

    try:
        submitted_time = float(form_timestamp)
        elapsed = time.time() - submitted_time

        if elapsed < min_seconds:
            logger.warning(
                f"Time trap triggered - form submitted in {elapsed:.1f}s from IP: {get_client_ip(request)}"
            )
            return True
    except (ValueError, TypeError):
        logger.warning(f"Invalid timestamp from IP: {get_client_ip(request)}")
        return True

    return False


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")
