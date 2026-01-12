"""
Hosting App Views

Handles the managed hosting signup flow:
- signup: Form to choose subdomain, store name, email
- signup_success: After successful Stripe payment
- signup_cancelled: If user cancels Stripe checkout

The actual provisioning happens via the provisioner service API.
"""

from django.shortcuts import render
from django.conf import settings
from django.views.decorators.http import require_GET


def signup(request):
    """
    Main signup page for managed hosting.
    The form is handled client-side with JavaScript that calls the provisioner API.
    """
    context = {
        "provisioner_api_url": getattr(
            settings, "PROVISIONER_API_URL", "https://provisioner.djangify.com/api"
        ),
        "ebuilder_domain": getattr(settings, "EBUILDER_DOMAIN", "djangify.com"),
    }
    return render(request, "hosting/signup.html", context)


def signup_success(request):
    """
    Success page after Stripe checkout completes.
    Stripe redirects here with session_id parameter.
    """
    session_id = request.GET.get("session_id")
    subdomain = request.GET.get("subdomain")

    context = {
        "session_id": session_id,
        "subdomain": subdomain,
        "store_url": f"https://{subdomain}.{getattr(settings, 'EBUILDER_DOMAIN', 'djangify.com')}"
        if subdomain
        else None,
    }
    return render(request, "hosting/signup_success.html", context)


def signup_cancelled(request):
    """
    Page shown when user cancels Stripe checkout.
    """
    return render(request, "hosting/signup_cancelled.html")
