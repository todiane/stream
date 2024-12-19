# stream/storage.py
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os


class SecureFileStorage(FileSystemStorage):
    def __init__(self):
        # Initialize with the secure downloads directory
        secure_root = os.path.join(settings.MEDIA_ROOT, "secure_downloads")
        super().__init__(location=secure_root, base_url=settings.MEDIA_URL)

    def get_valid_name(self, name):
        """
        Return a filename without 'public/' prefix
        """
        name = super().get_valid_name(name)
        return name.replace("public/", "")


class PublicMediaStorage(FileSystemStorage):
    def __init__(self):
        # Initialize with the public media directory
        public_root = settings.PUBLIC_MEDIA_ROOT
        super().__init__(
            location=public_root, base_url=settings.MEDIA_URL + settings.MEDIA_PREFIX
        )

    def get_valid_name(self, name):
        """
        Return a filename without 'public/' prefix
        """
        name = super().get_valid_name(name)
        return name.replace("public/", "")

    def url(self, name):
        """
        Return URL including the public directory
        """
        url = super().url(name)
        if not url.startswith("/media/public/"):
            url = url.replace("/media/", "/media/public/")
        return url


# Create instances of storage classes
secure_storage = SecureFileStorage()
public_storage = PublicMediaStorage()
