"""
Management command to create admin user from environment variables.
Used by provisioner for automated instance setup.

Usage:
    python manage.py create_admin_from_env

Environment variables:
    ADMIN_EMAIL - Email address for the admin user
    ADMIN_PASSWORD - Password for the admin user
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress


class Command(BaseCommand):
    help = "Create admin user from ADMIN_EMAIL and ADMIN_PASSWORD environment variables"

    def handle(self, *args, **options):
        User = get_user_model()

        email = os.environ.get("ADMIN_EMAIL")
        password = os.environ.get("ADMIN_PASSWORD")

        if not email:
            self.stdout.write(
                self.style.WARNING("ADMIN_EMAIL not set, skipping admin creation")
            )
            return

        if not password:
            self.stdout.write(
                self.style.WARNING("ADMIN_PASSWORD not set, skipping admin creation")
            )
            return

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.SUCCESS(f"Admin user {email} already exists"))
            return

        # Create the user
        user = User.objects.create_superuser(email=email, password=password)

        # Mark email as verified (so they can log in immediately)
        EmailAddress.objects.create(user=user, email=email, verified=True, primary=True)

        self.stdout.write(self.style.SUCCESS(f"Created admin user: {email}"))
