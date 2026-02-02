from django.core.management.base import BaseCommand
from shop.models import ShopSettings


class Command(BaseCommand):
    help = "Configure site as demo mode (for sites being built for sale)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--disable",
            action="store_true",
            help="Disable demo mode (convert to live site)",
        )

    def handle(self, *args, **options):
        settings, created = ShopSettings.objects.get_or_create(id=1)

        if options["disable"]:
            settings.is_demo_site = False
            settings.save()
            self.stdout.write(
                self.style.SUCCESS("✓ Demo mode DISABLED - site is now LIVE")
            )
            self.stdout.write(
                self.style.WARNING("⚠ Ensure Stripe credentials are configured!")
            )
        else:
            settings.is_demo_site = True
            # Don't clear existing Stripe keys - just flag as demo
            settings.save()
            self.stdout.write(
                self.style.SUCCESS("✓ Demo mode ENABLED - Stripe payments disabled")
            )
            self.stdout.write(
                "Site is now in demo mode. Stripe configuration required before accepting payments."
            )
