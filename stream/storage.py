from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os


class SecureFileStorage(FileSystemStorage):
    def __init__(self):
        # Initialize with the secure downloads directory
        secure_root = os.path.join(settings.MEDIA_ROOT, "secure_downloads")
        super().__init__(location=secure_root)

    def _save(self, name, content):
        # Ensure the file is saved with strict permissions
        file_path = super()._save(name, content)
        full_path = os.path.join(self.location, file_path)
        os.chmod(full_path, 0o640)  # User rw, group r, others none
        return file_path


class PublicMediaStorage(FileSystemStorage):
    def __init__(self):
        # Initialize with the public media directory
        public_root = os.path.join(settings.MEDIA_ROOT, "public")
        super().__init__(location=public_root)

    def _save(self, name, content):
        # Save with standard web-accessible permissions
        file_path = super()._save(name, content)
        full_path = os.path.join(self.location, file_path)
        os.chmod(full_path, 0o644)  # User rw, group r, others r
        return file_path


# Create storage instances
secure_storage = SecureFileStorage()
public_storage = PublicMediaStorage()
