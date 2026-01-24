# shop/fields.py
"""
Custom model fields for eBuilder.
Includes EncryptedCharField for storing sensitive data.
"""

from django.db import models
from django import forms

from .encryption import encrypt_value, decrypt_value


class EncryptedCharField(models.CharField):
    """
    A CharField that encrypts data at rest using Fernet encryption.
    Values are encrypted before saving and decrypted when retrieved.

    Note: Encrypted values are longer than plaintext, so max_length
    should account for this (typically 2-3x the plaintext length).
    """

    description = "An encrypted string"

    def __init__(self, *args, **kwargs):
        # Default to longer max_length for encrypted data
        kwargs.setdefault("max_length", 500)
        kwargs.setdefault("blank", True)
        kwargs.setdefault("default", "")
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        """Encrypt value before saving to database."""
        if value is None or value == "":
            return ""

        # Don't re-encrypt already encrypted values
        if self._is_encrypted(value):
            return value

        try:
            return encrypt_value(value)
        except Exception:
            # If encryption fails, store empty (don't store plaintext)
            return ""

    def from_db_value(self, value, expression, connection):
        """Decrypt value when reading from database."""
        if value is None or value == "":
            return ""
        return decrypt_value(value)

    def to_python(self, value):
        """Convert value to Python string."""
        if value is None:
            return ""
        return str(value)

    def _is_encrypted(self, value):
        """
        Check if value appears to be already encrypted.
        Encrypted values are base64 and start with 'gAAAAA' (Fernet signature).
        """
        if not value or len(value) < 50:
            return False
        try:
            # Fernet tokens are base64 and have a specific structure
            import base64

            decoded = base64.urlsafe_b64decode(value.encode("utf-8"))
            # Check for Fernet version byte
            return decoded[0:1] == b"\x80"
        except Exception:
            return False

    def formfield(self, **kwargs):
        """Use password input in forms by default."""
        defaults = {
            "widget": forms.PasswordInput(
                attrs={
                    "autocomplete": "new-password",
                    "class": "vTextField",
                }
            ),
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)


class EncryptedTextField(models.TextField):
    """
    A TextField variant for longer encrypted content.
    Same encryption behavior as EncryptedCharField.
    """

    description = "An encrypted text field"

    def get_prep_value(self, value):
        if value is None or value == "":
            return ""
        try:
            return encrypt_value(value)
        except Exception:
            return ""

    def from_db_value(self, value, expression, connection):
        if value is None or value == "":
            return ""
        return decrypt_value(value)

    def to_python(self, value):
        if value is None:
            return ""
        return str(value)

    def formfield(self, **kwargs):
        defaults = {
            "widget": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "vLargeTextField",
                }
            ),
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)
