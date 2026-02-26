# stream/storage.py

from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os


class SecureFileStorage(FileSystemStorage):
    def __init__(self):
        secure_root = os.path.join(settings.MEDIA_ROOT, "secure_downloads")
        super().__init__(
            location=secure_root,
            base_url=settings.MEDIA_URL + "secure_downloads/",
        )


class PublicMediaStorage(FileSystemStorage):
    def __init__(self):
        public_root = os.path.join(settings.MEDIA_ROOT, "public")
        super().__init__(
            location=public_root,
            base_url=settings.MEDIA_URL + "public/",
        )

    def url(self, name):
        return super().url(name)


secure_storage = SecureFileStorage()
public_storage = PublicMediaStorage()
