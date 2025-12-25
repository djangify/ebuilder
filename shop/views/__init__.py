# shop/views/__init__.py
from .catalog import (
    product_list,
    product_detail,
    category_hub,
    category_list,
)

from .cart import (
    cart_add,
    cart_detail,
    cart_remove,
    cart_update,
)

from .checkout import (
    checkout,
    payment_success,
    payment_cancel,
    stripe_webhook,
)

from .downloads import (
    secure_download,
    purchases,
    order_history,
    order_detail,
)

from .reviews import add_review

from .wishlist import (
    toggle_wishlist,
    wishlist_list,
)
