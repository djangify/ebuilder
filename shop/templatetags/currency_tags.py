# shop/templatetags/currency_tags.py
from django import template
from pages.models import SiteSettings

register = template.Library()


@register.filter
def currency(value):
    """
    Format a value with the site's currency symbol.
    Usage: {{ price|currency }}
    """
    try:
        settings = SiteSettings.objects.first()
        symbol = settings.currency_symbol if settings else "£"
    except Exception:
        symbol = "£"

    try:
        # Handle Decimal and float values
        formatted = f"{float(value):.2f}"
        return f"{symbol}{formatted}"
    except (ValueError, TypeError):
        return f"{symbol}0.00"


@register.simple_tag
def currency_symbol():
    """
    Return just the currency symbol.
    Usage: {% currency_symbol %}
    """
    try:
        settings = SiteSettings.objects.first()
        return settings.currency_symbol if settings else "£"
    except Exception:
        return "£"
