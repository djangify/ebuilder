# shop/management/commands/generate_encryption_key.py
"""
Management command to generate a Fernet encryption key.
Usage: python manage.py generate_encryption_key
"""

from django.core.management.base import BaseCommand
from cryptography.fernet import Fernet


class Command(BaseCommand):
    help = "Generate a new Fernet encryption key for ENCRYPTION_KEY in .env"

    def handle(self, *args, **options):
        key = Fernet.generate_key().decode("utf-8")

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("Generated new ENCRYPTION_KEY:"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write("")
        self.stdout.write(self.style.WARNING(key))
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write("")
        self.stdout.write("Add this to your .env file:")
        self.stdout.write("")
        self.stdout.write(self.style.HTTP_INFO(f"ENCRYPTION_KEY={key}"))
        self.stdout.write("")
        self.stdout.write(self.style.NOTICE("⚠️  IMPORTANT:"))
        self.stdout.write(
            "  - Store this key securely - losing it means losing encrypted data"
        )
        self.stdout.write("  - Never commit this key to version control")
        self.stdout.write(
            "  - Use the same key across all deployments accessing the same database"
        )
        self.stdout.write("")
