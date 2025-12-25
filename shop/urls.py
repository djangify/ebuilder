# shop/urls.py
from django.urls import path
from . import views, webhooks
from django.views.generic import TemplateView
from .views.wishlist import remove_from_wishlist


app_name = "shop"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("category/<slug:slug>/", views.category_list, name="category"),
    path("category/", views.category_hub, name="category_hub"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    # Cart
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("cart/update/<int:product_id>/", views.cart_update, name="cart_update"),
    # Checkout
    path("checkout/", views.checkout, name="checkout"),
    path("success/", views.payment_success, name="payment_success"),
    path("cancel/", views.payment_cancel, name="payment_cancel"),
    # Stripe webhook
    path("webhook/", webhooks.stripe_webhook, name="stripe_webhook"),
    # Secure downloads (uses ProductDownload model)
    path(
        "secure-download/<int:order_item_id>/<int:download_id>/",
        views.secure_download,
        name="secure_download",
    ),
    # Orders / Purchases
    path("orders/", views.order_history, name="order_history"),
    path("orders/<str:order_id>/", views.order_detail, name="order_detail"),
    path("purchases/", views.purchases, name="purchases"),
    # Reviews
    path("product/<int:product_id>/review/", views.add_review, name="add_review"),
    # Wishlist
    path(
        "wishlist/toggle/<int:product_id>/",
        views.toggle_wishlist,
        name="wishlist_toggle",
    ),
    path("wishlist/", views.wishlist_list, name="wishlist_list"),
    path(
        "wishlist/remove/<int:product_id>/",
        remove_from_wishlist,
        name="remove_from_wishlist",
    ),
    # Preview
    path(
        "success-preview/",
        TemplateView.as_view(template_name="shop/success.html"),
    ),
]
