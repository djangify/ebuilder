# shop/emails.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from pages.models import SiteSettings
import logging

logger = logging.getLogger("shop.emails")


def get_email_context():
    """
    Get common context variables for all shop emails.
    Returns site settings that should be available in every email template.
    """
    try:
        site_settings = SiteSettings.objects.first()
    except Exception:
        site_settings = None

    if site_settings:
        return {
            "homepage_settings": site_settings,
            "site_settings": site_settings,
            "site_name": site_settings.business_name,
            "site_url": site_settings.site_url,
            "support_email": site_settings.support_email,
            "business_name": site_settings.business_name,
            "currency_symbol": site_settings.currency_symbol,
            "currency_code": site_settings.currency_code,
        }
    else:
        # Fallbacks if SiteSettings doesn't exist
        return {
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


def send_order_confirmation_email(order):
    """Send order confirmation email to customer."""
    try:
        logger.info(f"Preparing order confirmation email for order {order.order_id}")

        # Get base context with site settings
        context = get_email_context()

        items_data = [
            {
                "name": item.product.title,
                "price": (item.price_paid_pence * item.quantity) / 100,
                "quantity": item.quantity,
                "downloads_remaining": item.downloads_remaining,
            }
            for item in order.items.all()
        ]

        # Add order-specific context
        context.update(
            {
                "order_id": order.order_id,
                "first_name": order.user.first_name if order.user else "",
                "email": order.email,
                "items": items_data,
                "total": order.total_price,
                "user_name": order.user.get_full_name() if order.user else None,
                "date_created": order.created.strftime("%Y-%m-%d %H:%M:%S"),
                # Build absolute login URL
                "login_url": f"{context['site_url']}/accounts/login/",
                "dashboard_url": f"{context['site_url']}/accounts/dashboard/",
            }
        )

        logger.info(f"Rendering template for order {order.order_id}")

        html_content = render_to_string(
            "account/email/order_confirmation.html", context
        )
        text_content = strip_tags(html_content)

        subject = f"Order Confirmation #{order.order_id}"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [order.email]

        logger.info(f"Sending email from {from_email} to {recipient_list}")

        msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        logger.info(
            f"Order confirmation email sent successfully for order {order.order_id} to {order.email}"
        )

    except Exception as e:
        logger.error(
            f"Failed to send order confirmation email for order {order.order_id}: {str(e)}",
            exc_info=True,
        )
        raise


def send_admin_new_order_email(order):
    """Send notification email to admin when a new order is placed."""
    try:
        logger.info(f"Preparing admin notification email for order {order.order_id}")

        # Get base context with site settings
        context = get_email_context()

        items_data = [
            {
                "name": item.product.title,
                "price": (item.price_paid_pence * item.quantity) / 100,
                "quantity": item.quantity,
            }
            for item in order.items.all()
        ]

        # Add order-specific context
        context.update(
            {
                "order_id": order.order_id,
                "customer_email": order.email,
                "customer_name": order.user.get_full_name() if order.user else "Guest",
                "items": items_data,
                "total": order.total_price,
                "date_created": order.created.strftime("%Y-%m-%d %H:%M:%S"),
                # Admin link to order
                "admin_url": f"{context['site_url']}/admin/shop/order/{order.id}/change/",
            }
        )

        logger.info(f"Rendering admin template for order {order.order_id}")

        html_content = render_to_string("account/email/admin_new_order.html", context)
        text_content = strip_tags(html_content)

        subject = f"New Order #{order.order_id}"
        from_email = settings.DEFAULT_FROM_EMAIL
        admin_email = getattr(settings, "ADMIN_EMAIL", settings.DEFAULT_FROM_EMAIL)

        logger.info(f"Sending admin email from {from_email} to {admin_email}")

        msg = EmailMultiAlternatives(subject, text_content, from_email, [admin_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        logger.info(f"Admin notification sent for order {order.order_id}")

    except Exception as e:
        logger.error(
            f"Failed to send admin notification for order {order.order_id}: {str(e)}",
            exc_info=True,
        )
        raise
