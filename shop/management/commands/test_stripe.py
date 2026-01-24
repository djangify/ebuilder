# shop/management/commands/test_stripe.py
"""
Management command to test Stripe API connection.
Usage: python manage.py test_stripe
"""

from django.core.management.base import BaseCommand

import stripe

from shop.config_manager import ConfigManager


class Command(BaseCommand):
    help = "Test Stripe API connection using configured credentials"

    def handle(self, *args, **options):
        self.stdout.write("\nTesting Stripe connection...\n")

        config = ConfigManager.get_stripe_config()

        # Check if configured
        if not config["secret_key"]:
            self.stdout.write(
                self.style.ERROR(
                    "✗ Stripe secret key not configured\n"
                    "  Set STRIPE_SECRET_KEY in .env or configure in Admin > Shop Settings"
                )
            )
            return

        # Mask the key for display
        key_preview = config["secret_key"][:12] + "..." + config["secret_key"][-4:]
        self.stdout.write(f"Using key: {key_preview}")
        self.stdout.write(f"Mode: {'LIVE' if config['live_mode'] else 'TEST'}")

        # Test API connection
        stripe.api_key = config["secret_key"]

        try:
            # Retrieve account to test connection
            account = stripe.Account.retrieve()

            self.stdout.write(self.style.SUCCESS("\n✓ Stripe connection successful!"))
            self.stdout.write(f"  Account ID: {account.id}")
            self.stdout.write(
                f"  Business: {account.get('business_profile', {}).get('name', 'N/A')}"
            )
            self.stdout.write(f"  Country: {account.country}")
            self.stdout.write(f"  Currency: {account.default_currency}")

            # Check if charges are enabled
            if account.charges_enabled:
                self.stdout.write(self.style.SUCCESS("  Charges: Enabled"))
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "  Charges: Disabled (account may need verification)"
                    )
                )

        except stripe.error.AuthenticationError as e:
            self.stdout.write(
                self.style.ERROR(f"\n✗ Authentication failed: {e.user_message}")
            )
            self.stdout.write("  Check your API key is correct")

        except stripe.error.APIConnectionError as e:
            self.stdout.write(
                self.style.ERROR(f"\n✗ Connection failed: {e.user_message}")
            )
            self.stdout.write("  Check your network connection")

        except stripe.error.StripeError as e:
            self.stdout.write(self.style.ERROR(f"\n✗ Stripe error: {e.user_message}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n✗ Unexpected error: {e}"))

        self.stdout.write("")
