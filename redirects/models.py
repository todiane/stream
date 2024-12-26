from django.db import models
from django.core.exceptions import ValidationError
import re


class URLRedirect(models.Model):
    old_path = models.CharField(max_length=255, unique=True)
    new_path = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Remove leading/trailing slashes for consistency
        if self.old_path:
            self.old_path = self.old_path.strip("/")
            # Check for non-latin1 characters
            try:
                self.old_path.encode("latin-1")
            except UnicodeEncodeError:
                raise ValidationError(
                    {
                        "old_path": "Path contains unsupported characters. Please use only basic letters, numbers and hyphens."
                    }
                )

        if self.new_path:
            self.new_path = self.new_path.strip("/")
            try:
                self.new_path.encode("latin-1")
            except UnicodeEncodeError:
                raise ValidationError(
                    {
                        "new_path": "Path contains unsupported characters. Please use only basic letters, numbers and hyphens."
                    }
                )

        # Validate URL lengths
        if len(self.old_path) > 255:
            raise ValidationError(
                {
                    "old_path": f"URL is too long ({len(self.old_path)} characters). Maximum length is 255 characters."
                }
            )
        if len(self.new_path) > 255:
            raise ValidationError(
                {
                    "new_path": f"URL is too long ({len(self.new_path)} characters). Maximum length is 255 characters."
                }
            )

        # Check for existing redirects
        existing = URLRedirect.objects.filter(old_path=self.old_path)
        if existing.exists() and (not self.pk or existing.first().pk != self.pk):
            raise ValidationError(
                {"old_path": f'A redirect from "{self.old_path}" already exists'}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.old_path} to {self.new_path}"

    class Meta:
        verbose_name = "URL Redirect"
        verbose_name_plural = "URL Redirects"
