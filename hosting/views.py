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


# Configuration - pulls from Django settings with sensible defaults
PROVISIONER_API_URL = getattr(
    settings, 'PROVISIONER_API_URL', 'https://provisioner.ebuilder.host/api'
)
EBUILDER_DOMAIN = getattr(settings, 'EBUILDER_DOMAIN', 'ebuilder.host')


def signup(request):
    """
    Main signup page with form for subdomain, store name, and email.
    
    The form uses JavaScript to:
    1. Check subdomain availability via provisioner API
    2. Create Stripe checkout session via provisioner API
    3. Redirect to Stripe Checkout
    """
    context = {
        'provisioner_api_url': PROVISIONER_API_URL,
        'ebuilder_domain': EBUILDER_DOMAIN,
        'page_title': 'Sign Up for Managed Hosting',
    }
    return render(request, 'hosting/signup.html', context)


@require_GET
def signup_success(request):
    """
    Success page shown after Stripe checkout completes.
    
    Query params:
    - session_id: Stripe checkout session ID
    - subdomain: The subdomain they chose
    
    The provisioner handles the actual container creation via webhook.
    """
    session_id = request.GET.get('session_id', '')
    subdomain = request.GET.get('subdomain', '')
    
    # Construct the store URL for display
    store_url = f"https://{subdomain}.{EBUILDER_DOMAIN}" if subdomain else None
    
    context = {
        'session_id': session_id,
        'subdomain': subdomain,
        'store_url': store_url,
        'ebuilder_domain': EBUILDER_DOMAIN,
        'page_title': 'Welcome to eBuilder!',
    }
    return render(request, 'hosting/success.html', context)


@require_GET
def signup_cancelled(request):
    """
    Page shown when user cancels Stripe checkout.
    
    No payment was taken - just offer them a way to try again.
    """
    context = {
        'page_title': 'Payment Cancelled',
    }
    return render(request, 'hosting/cancelled.html', context)
