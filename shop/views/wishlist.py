# shop/views/wishlist.py
from ..models import Product
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from ..models import WishList


from django.http import JsonResponse


@login_required
@require_POST
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    existing = WishList.objects.filter(user=request.user, product=product)

    if existing.exists():
        existing.delete()
        is_favourite = False
    else:
        WishList.objects.create(user=request.user, product=product)
        is_favourite = True

    # If AJAX request → return JSON
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse(
            {
                "status": "success",
                "is_favourite": is_favourite,
            }
        )

    # Fallback for non-JS (normal form POSTs)
    return redirect(request.META.get("HTTP_REFERER", "shop:product_list"))


@login_required
def wishlist_list(request):
    items = WishList.objects.filter(user=request.user).select_related("product")

    favourite_products = [item.product for item in items]

    return render(
        request,
        "accounts/includes/dashboard_wishlist.html",
        {"favourite_products": favourite_products},
    )


@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    WishList.objects.filter(user=request.user, product_id=product_id).delete()

    return redirect("accounts:dashboard")
