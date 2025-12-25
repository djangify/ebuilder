# shop/emails.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger("shop.emails")


def send_order_confirmation_email(order):
    """Send order confirmation email to customer."""
    try:
        logger.info(f"Preparing order confirmation email for order {order.order_id}")

        items_data = [
            {
                "name": item.product.title,
                "price": (item.price_paid_pence * item.quantity) / 100,
                "quantity": item.quantity,
                "downloads_remaining": item.downloads_remaining,
            }
            for item in order.items.all()
        ]

        context = {
            "order_id": order.order_id,
            "first_name": order.user.first_name if order.user else "",
            "email": order.email,
            "items": items_data,
            "total": order.total_price,
            "site_url": getattr(settings, "SITE_URL", "{{ site_url }}"),
            "user_name": order.user.get_full_name() if order.user else None,
            "date_created": order.created.strftime("%Y-%m-%d %H:%M:%S"),
        }

        logger.info(f"Rendering template for order {order.order_id}")

        # Use correct template path
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
            exc_info=True,  # This logs the full stack trace
        )
        raise


def send_admin_new_order_email(order):
    """Send notification email to admin when a new order is placed."""
    try:
        logger.info(f"Preparing admin notification email for order {order.order_id}")

        items_data = [
            {
                "name": item.product.title,
                "price": (item.price_paid_pence * item.quantity) / 100,
                "quantity": item.quantity,
            }
            for item in order.items.all()
        ]

        context = {
            "order_id": order.order_id,
            "customer_email": order.email,
            "customer_name": order.user.get_full_name() if order.user else "Guest",
            "items": items_data,
            "total": order.total_price,
            "site_url": getattr(settings, "SITE_URL", "{{ site_url }}"),
            "date_created": order.created.strftime("%Y-%m-%d %H:%M:%S"),
        }

        logger.info(f"Rendering admin template for order {order.order_id}")

        # Use correct template path
        html_content = render_to_string("account/email/admin_new_order.html", context)
        text_content = strip_tags(html_content)

        subject = f"💰 New Order #{order.order_id}"
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
            exc_info=True,  # This logs the full stack trace
        )
        raise
