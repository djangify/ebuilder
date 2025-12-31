# shop/views/catalog.py
from ..models import Category, Product, OrderItem
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.paginator import Paginator
import stripe
from django.db.models import Q, Count
import logging
from shop.forms import ProductReviewForm
from ..models import WishList
from ..models import ShopSettings, ShopPromoBlock


stripe.api_key = settings.STRIPE_SECRET_KEY

# Set up logger
logger = logging.getLogger("shop")


def product_list(request):
    """
    Shop product list page with customisable homepage sections.
    Uses ShopSettings for hero, intro, spotlight, promo blocks and display options.
    """
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category")

    # Get shop settings (create default if none exists)
    shop_settings = ShopSettings.objects.first()
    if not shop_settings:
        shop_settings = ShopSettings.objects.create()

    # Base product queryset
    products = Product.objects.filter(
        is_active=True, status__in=["publish", "soon", "full"]
    )

    # Apply display mode filtering
    if shop_settings.product_display_mode == "featured":
        products = products.filter(featured=True)
    elif (
        shop_settings.product_display_mode == "category"
        and shop_settings.display_category
    ):
        products = products.filter(category=shop_settings.display_category)

    # Apply URL-based category filter (overrides display mode if present)
    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)

    # Apply search filter
    if query:
        products = products.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    # Order and paginate
    products = products.order_by("order", "-created")
    paginator = Paginator(products, shop_settings.products_per_page)
    page = request.GET.get("page")
    products = paginator.get_page(page)

    # Get categories for filter sidebar
    categories = Category.objects.annotate(
        product_count=Count(
            "product",
            filter=Q(
                product__is_active=True,
                product__status__in=["publish", "soon", "full"],
            ),
        )
    ).filter(product_count__gt=0)

    # Get promo blocks if enabled
    promo_blocks = None
    if shop_settings.show_promo_blocks:
        promo_blocks = shop_settings.promo_blocks.filter(published=True)

    return render(
        request,
        "shop/list.html",
        {
            "products": products,
            "categories": categories,
            "current_category": current_category,
            "query": query,
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
            # Shop Settings context
            "shop_settings": shop_settings,
            "promo_blocks": promo_blocks,
            "breadcrumbs": [
                {"title": "Shop", "url": None},
            ],
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug,
        is_active=True,
        status__in=["publish", "soon", "full"],
    )

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

    order_item = None
    has_purchased = False
    review_form = None

    if request.user.is_authenticated:
        order_item = OrderItem.objects.filter(
            order__user=request.user,
            order__paid=True,
            product=product,
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
            "breadcrumbs": [
                {"title": "Shop", "url": "/shop/"},
                {
                    "title": product.category.name,
                    "url": product.category.get_absolute_url(),
                },
                {"title": product.title, "url": None},
            ],
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
        category=category,
        status__in=["publish", "soon", "full"],
        is_active=True,
    ).order_by("order", "-created")

    paginator = Paginator(products, 12)
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
            "breadcrumbs": [
                {"title": "Shop", "url": "/shop/"},
                {"title": category.name, "url": None},
            ],
        },
    )
