# shop/views/checkout.py
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from ..models import Order, OrderItem
from pages.models import SiteSettings
from ..emails import send_order_confirmation_email
from ..cart import Cart
from ..config_manager import ConfigManager
import stripe
import logging

# Set up logger
logger = logging.getLogger("shop")


def checkout(request):
    """
    Display checkout page with Stripe payment form.
    Requires authenticated user.
    """
    if not request.user.is_authenticated:
        return redirect("account_login")

    # Check if demo mode or Stripe not configured
    stripe_config = ConfigManager.get_stripe_config()
    if stripe_config is None:
        messages.error(
            request,
            "Payment processing is not available at this time. Please contact the store owner.",
        )
        return redirect("shop:cart_detail")

    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, "Your cart is empty.")
        return redirect("shop:cart_detail")

    try:
        total_price = cart.get_total_price()

        if total_price <= 0:
            messages.error(request, "Invalid cart total")
            return redirect("shop:cart_detail")

        # Get currency from SiteSettings, fallback to settings, then to 'gbp'
        try:
            site_settings = SiteSettings.objects.first()
            currency = site_settings.currency_code.lower() if site_settings else "gbp"
        except Exception:
            currency = getattr(settings, "STRIPE_CURRENCY", "gbp")

        # Create a new PaymentIntent each time user loads checkout
        stripe.api_key = stripe_config["secret_key"]
        intent = stripe.PaymentIntent.create(
            amount=int(total_price * 100),
            currency=currency,  # Now uses database setting
            automatic_payment_methods={"enabled": False},
            metadata={
                "user_id": str(request.user.id),
            },
            receipt_email=request.user.email,
        )

        context = {
            "client_secret": intent.client_secret,
            "STRIPE_PUBLIC_KEY": stripe_config["public_key"],
            "cart": cart,
            "payment_intent_id": intent.id,
        }
        return render(request, "shop/checkout.html", context)

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error during checkout: {str(e)}")
        messages.error(request, f"Payment processing error: {str(e)}")
        return redirect("shop:cart_detail")

    except Exception as e:
        logger.error(f"Unexpected checkout error: {str(e)}")
        messages.error(request, "An error occurred during checkout. Please try again.")
        return redirect("shop:cart_detail")


def payment_success(request):
    """
    Handle successful payment.
    Creates order, sends confirmation email, shows success page.
    Downloads are accessed via dashboard - no download links sent.
    """
    payment_intent_id = request.GET.get("payment_intent")
    if not payment_intent_id:
        messages.error(request, "No payment information found.")
        return redirect("shop:cart_detail")

    try:
        stripe_config = ConfigManager.get_stripe_config()
        stripe.api_key = stripe_config["secret_key"]
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        if payment_intent.status != "succeeded":
            messages.error(request, "Payment was not successful.")
            return redirect("shop:cart_detail")

        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to complete checkout.")
            return redirect("account_login")

        # Prevent duplicate orders
        existing_order = Order.objects.filter(
            payment_intent_id=payment_intent_id
        ).first()
        if existing_order:
            return redirect("shop:purchases")

        cart = Cart(request)

        # Create the order
        order = Order.objects.create(
            user=request.user,
            email=request.user.email,
            payment_intent_id=payment_intent_id,
            paid=True,
            status="completed",
        )

        # Create order items
        for item in cart:
            # Get the purchased download if specified
            purchased_download = None
            if item.get("download_id"):
                from ..models import ProductDownload

                try:
                    purchased_download = ProductDownload.objects.get(
                        id=item["download_id"]
                    )
                except ProductDownload.DoesNotExist:
                    pass

            OrderItem.objects.create(
                order=order,
                product=item["product"],
                purchased_download=purchased_download,
                price_paid_pence=int(item["price"] * 100),
                quantity=item["quantity"],
            )

            # Update product purchase count
            product = item["product"]
            product.purchase_count += item["quantity"]
            product.save()

        # Send emails - order confirmation only, no download links
        try:
            send_order_confirmation_email(order)
            from ..emails import send_admin_new_order_email

            send_admin_new_order_email(order)
        except Exception as e:
            logger.error(f"Error sending emails for order {order.order_id}: {str(e)}")

        cart.clear()

        return render(request, "shop/success.html", {"order": order})

    except Exception as e:
        logger.error(f"Error in payment_success: {str(e)}")
        messages.error(request, "There was an error processing your order.")
        return redirect("shop:cart_detail")


def payment_cancel(request):
    """Handle cancelled payment."""
    messages.error(request, "Payment was cancelled.")
    return redirect("shop:cart_detail")
