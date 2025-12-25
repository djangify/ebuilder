# shop/views/cart.py
from ..models import Product, ProductDownload
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
import stripe
import logging
from ..cart import Cart


stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger("shop")


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    quantity = int(request.POST.get("quantity", 1))
    download_id = request.POST.get("download_id")

    # Validate download belongs to this product
    if download_id:
        download = get_object_or_404(ProductDownload, id=download_id, product=product)
        download_id = download.id
    else:
        download_id = None

    cart.add(product=product, quantity=quantity, download_id=download_id)

    messages.success(request, f"{product.title} has been added to your cart.")
    return redirect("shop:cart_detail")


def cart_detail(request):
    try:
        cart = Cart(request)
        return render(request, "shop/cart.html", {"cart": cart})
    except Exception as e:
        print(f"Error in cart detail: {str(e)}")
        messages.error(request, "There was an error displaying your cart.")
        return redirect("shop:product_list")


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    download_id = request.POST.get("download_id")
    cart.remove(product, download_id=download_id)
    return redirect("shop:cart_detail")


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get("quantity", 1))
    download_id = request.POST.get("download_id")
    cart.add(
        product=product,
        quantity=quantity,
        override_quantity=True,
        download_id=download_id,
    )
    return redirect("shop:cart_detail")
