# shop/views/catalog.py
from ..models import Category, Product, OrderItem
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.paginator import Paginator
import stripe
from django.db.models import Q
import logging
from shop.forms import ProductReviewForm
from ..models import WishList


stripe.api_key = settings.STRIPE_SECRET_KEY

# Set up logger
logger = logging.getLogger("shop")


def product_list(request):
    """
    Standard shop product list page.
    Shows all published and active products.
    Supports optional search + category filtering.
    """
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category")

    products = Product.objects.filter(
        is_active=True, status__in=["publish", "soon", "full"]
    ).order_by("order", "-created")

    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)

    if query:
        products = products.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    paginator = Paginator(products, 12)  # 12 per page
    page = request.GET.get("page")
    products = paginator.get_page(page)

    categories = Category.objects.all()

    return render(
        request,
        "shop/list.html",
        {
            "products": products,
            "categories": categories,
            "current_category": current_category,
            "query": query,
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product, slug=slug, is_active=True, status__in=["publish", "soon", "full"]
    )

    # Correct wishlist lookup
    wishlist_items = []
    if request.user.is_authenticated:
        wishlist_items = list(
            WishList.objects.filter(user=request.user).values_list(
                "product_id", flat=True
            )
        )

    related_products = Product.objects.filter(
        category=product.category,
        status__in=["publish", "full"],
        is_active=True,
    ).exclude(id=product.id)[:3]

    has_purchased = False
    order_item = None
    review_form = None

    if request.user.is_authenticated:
        order_item = OrderItem.objects.filter(
            order__user=request.user, order__paid=True, product=product
        ).first()

        has_purchased = bool(order_item)
        review_form = ProductReviewForm() if product.can_review(request.user) else None

    # Additional product images
    images = product.images.all()

    return render(
        request,
        "shop/detail.html",
        {
            "product": product,
            "wishlist_items": wishlist_items,
            "related_products": related_products,
            "has_purchased": has_purchased,
            "order_item": order_item,
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
            "form": review_form,
            "images": images,
            "request": request,
        },
    )


def category_hub(request):
    categories = Category.objects.filter(
        product__status__in=["publish", "soon", "full"], product__is_active=True
    ).distinct()
    return render(request, "shop/category_hub.html", {"categories": categories})


def category_list(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(
        category=category, status__in=["publish", "soon", "full"], is_active=True
    ).order_by("order", "-created")

    paginator = Paginator(products, 12)  # adjust per row layout
    page = request.GET.get("page")
    products = paginator.get_page(page)

    return render(
        request,
        "shop/category.html",
        {
            "category": category,
            "products": products,
            "current_category": category,
            "hide_featured": True,
        },
    )
