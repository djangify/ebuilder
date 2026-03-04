from shop.models import ShopSettings
from content.models import ContentContainer


def create_shop_settings(sender, **kwargs):
    if not ShopSettings.objects.exists():
        container = ContentContainer.objects.create(name="Shop Container")
        ShopSettings.objects.create(content_container=container)
