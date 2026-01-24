# shop/encryption.py
"""
Fernet encryption utilities for sensitive configuration data.
Uses ENCRYPTION_KEY from environment variables.
"""

import base64
import logging
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

logger = logging.getLogger(__name__)


class EncryptionError(Exception):
    """Raised when encryption/decryption fails."""

    pass


@lru_cache(maxsize=1)
def get_fernet() -> Fernet | None:
    """
    Get cached Fernet instance using ENCRYPTION_KEY from settings/env.
    Returns None if key is not configured.
    """
    import os

    key = os.environ.get("ENCRYPTION_KEY") or getattr(settings, "ENCRYPTION_KEY", None)

    if not key:
        logger.warning("ENCRYPTION_KEY not configured - encrypted fields will not work")
        return None

    try:
        # Ensure key is bytes
        if isinstance(key, str):
            key = key.encode("utf-8")
        return Fernet(key)
    except Exception as e:
        logger.error(f"Invalid ENCRYPTION_KEY: {e}")
        return None


def encrypt_value(plaintext: str) -> str:
    """
    Encrypt a plaintext string using Fernet.
    Returns base64-encoded ciphertext.
    Raises EncryptionError if encryption fails.
    """
    if not plaintext:
        return ""

    fernet = get_fernet()
    if not fernet:
        raise EncryptionError("ENCRYPTION_KEY not configured")

    try:
        encrypted = fernet.encrypt(plaintext.encode("utf-8"))
        return base64.urlsafe_b64encode(encrypted).decode("utf-8")
    except Exception as e:
        raise EncryptionError(f"Encryption failed: {e}")


def decrypt_value(ciphertext: str) -> str:
    """
    Decrypt a base64-encoded ciphertext string.
    Returns plaintext string.
    Returns empty string if decryption fails or value is empty.
    """
    if not ciphertext:
        return ""

    fernet = get_fernet()
    if not fernet:
        logger.warning("Cannot decrypt: ENCRYPTION_KEY not configured")
        return ""

    try:
        # Decode from our base64 wrapper
        encrypted = base64.urlsafe_b64decode(ciphertext.encode("utf-8"))
        decrypted = fernet.decrypt(encrypted)
        return decrypted.decode("utf-8")
    except InvalidToken:
        logger.error("Decryption failed: Invalid token (wrong key or corrupted data)")
        return ""
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        return ""


def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key.
    Use this to create ENCRYPTION_KEY for .env file.
    """
    return Fernet.generate_key().decode("utf-8")


def is_encryption_configured() -> bool:
    """Check if encryption is properly configured."""
    return get_fernet() is not None
