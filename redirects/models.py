from django.db import models
from django.core.exceptions import ValidationError


class URLRedirect(models.Model):
    old_path = models.CharField(max_length=255, unique=True)
    new_path = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Remove leading/trailing slashes for consistency
        if self.old_path:
            self.old_path = self.old_path.strip("/")
        if self.new_path:
            self.new_path = self.new_path.strip("/")

        # Check for existing redirects
        existing = URLRedirect.objects.filter(old_path=self.old_path)
        if existing.exists() and (not self.pk or existing.first().pk != self.pk):
            raise ValidationError(
                {
                    "old_path": f'A redirect from "{self.old_path}" already exists and points to "{existing.first().new_path}"'
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.old_path} → {self.new_path}"

    class Meta:
        verbose_name = "URL Redirect"
        verbose_name_plural = "URL Redirects"
