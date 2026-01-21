from django.core.management.base import BaseCommand
from shop.models import Product


class Command(BaseCommand):
    help = "Creates a demo product if no products exist"

    def handle(self, *args, **options):
        if not Product.objects.exists():
            Product.objects.create(
                title="Demo Product - Getting Started",
                slug="demo-product-getting-started",
                description="This is a sample product to help you get started. Feel free to edit or delete it.",
                price_pence=1200,
                status="draft",
                is_active=False,
            )
            self.stdout.write(self.style.SUCCESS("✓ Demo product created"))
        else:
            self.stdout.write("Products already exist, skipping demo creation")
