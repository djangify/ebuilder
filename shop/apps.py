from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ShopConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shop"

    def ready(self):
        from .signals import create_shop_settings

        post_migrate.connect(create_shop_settings, sender=self)
