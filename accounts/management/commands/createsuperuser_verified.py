# accounts/management/commands/createsuperuser_verified.py
"""
Custom management command to create a superuser with verified email.
This combines createsuperuser + email verification in one step.

Usage:
    python manage.py createsuperuser_verified

Or in Docker:
    docker compose exec web python manage.py createsuperuser_verified
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
import getpass


class Command(BaseCommand):
    help = "Create a superuser with automatically verified email address"

    def handle(self, *args, **options):
        User = get_user_model()

        self.stdout.write("\n=== Create Verified Superuser ===\n")

        # Get email
        while True:
            email = input("Email address: ").strip()
            if not email:
                self.stdout.write(self.style.ERROR("Email cannot be empty."))
                continue
            if User.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.ERROR(f"User with email '{email}' already exists.")
                )
                continue
            break

        # Get password
        while True:
            password = getpass.getpass("Password: ")
            password_confirm = getpass.getpass("Password (again): ")

            if password != password_confirm:
                self.stdout.write(self.style.ERROR("Passwords don't match. Try again."))
                continue
            if len(password) < 8:
                self.stdout.write(
                    self.style.ERROR("Password must be at least 8 characters.")
                )
                continue
            break

        # Create superuser
        try:
            user = User.objects.create_superuser(email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Superuser created: {email}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating user: {e}"))
            return

        # Create and verify email address
        try:
            EmailAddress.objects.create(
                user=user, email=email, verified=True, primary=True
            )
            self.stdout.write(self.style.SUCCESS(f"Email verified: {email}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error verifying email: {e}"))
            return

        self.stdout.write(
            self.style.SUCCESS("\n✓ Superuser created and verified successfully!")
        )
        self.stdout.write("You can now log in at /admin/\n")
