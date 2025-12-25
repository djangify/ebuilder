# shop/cart.py
from decimal import Decimal
from django.conf import settings
from .models import Product, ProductDownload


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database.
        """
        product_ids = [item["product_id"] for item in self.cart.values()]
        products = Product.objects.filter(id__in=product_ids)
        products_dict = {str(p.id): p for p in products}

        download_ids = [
            item.get("download_id")
            for item in self.cart.values()
            if item.get("download_id")
        ]
        downloads = ProductDownload.objects.filter(id__in=download_ids)
        downloads_dict = {str(d.id): d for d in downloads}

        for key, item in self.cart.items():
            product = products_dict.get(str(item["product_id"]))
            if not product:
                continue

            cart_item = item.copy()
            cart_item["product"] = product
            cart_item["image_url"] = product.get_image_url()
            cart_item["price"] = Decimal(str(item["price"]))
            cart_item["total_price"] = cart_item["price"] * cart_item["quantity"]

            # Add the download object if it exists
            download_id = item.get("download_id")
            if download_id:
                cart_item["download"] = downloads_dict.get(str(download_id))
            else:
                cart_item["download"] = None

            yield cart_item

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def _get_cart_key(self, product_id, download_id=None):
        """Generate a unique key for product + download combination."""
        if download_id:
            return f"{product_id}_{download_id}"
        return str(product_id)

    def add(self, product, quantity=1, override_quantity=False, download_id=None):
        """
        Add a product to the cart with optional specific download variant.
        """
        cart_key = self._get_cart_key(product.id, download_id)

        if cart_key not in self.cart:
            self.cart[cart_key] = {
                "product_id": product.id,
                "download_id": download_id,
                "quantity": 0,
                "price": str(product.current_price),
            }

        if override_quantity:
            self.cart[cart_key]["quantity"] = quantity
        else:
            self.cart[cart_key]["quantity"] += quantity

        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product, download_id=None):
        """Remove a product from the cart."""
        cart_key = self._get_cart_key(product.id, download_id)
        if cart_key in self.cart:
            del self.cart[cart_key]
            self.save()

    def remove_by_key(self, cart_key):
        """Remove an item by its cart key."""
        if cart_key in self.cart:
            del self.cart[cart_key]
            self.save()

    def get_total_price(self):
        """Calculate total price of items in cart."""
        return sum(
            Decimal(str(item["price"])) * item["quantity"]
            for item in self.cart.values()
        )

    def clear(self):
        """Remove cart from session"""
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
