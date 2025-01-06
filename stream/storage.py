# stream/storage.py
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

class SecureFileStorage(FileSystemStorage):
    def __init__(self):
        secure_root = os.path.join(settings.MEDIA_ROOT, "secure_downloads")
        super().__init__(location=secure_root)

    def get_valid_name(self, name):
        name = super().get_valid_name(name)
        return name.replace("public/", "")

class PublicMediaStorage(FileSystemStorage):
    def __init__(self):
        public_root = os.path.join(settings.MEDIA_ROOT, "public")
        super().__init__(
            location=public_root,
            base_url='/media/public/'  # Changed this line to be explicit
        )

    def get_valid_name(self, name):
        name = super().get_valid_name(name)
        return name.replace("public/", "")

    def url(self, name):
        url = super().url(name)
        # Ensure URL starts with /media/public/
        if not url.startswith("/media/public/"):
            url = f"/media/public/{name}"
        return url

# Create instances
secure_storage = SecureFileStorage()
public_storage = PublicMediaStorage()