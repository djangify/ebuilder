# ebuilder/storage.py

from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os


class SecureStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(
            location=os.path.join(settings.MEDIA_ROOT, "secure"),
            base_url=settings.MEDIA_URL + "secure/",
        )


class PublicStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(
            location=os.path.join(settings.MEDIA_ROOT, "public"),
            base_url=settings.MEDIA_URL + "public/",
        )
