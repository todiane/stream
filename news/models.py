from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from stream.storage import public_storage
from django.utils import timezone
from tinymce.models import HTMLField  # type: ignore


class Author(models.Model):
    """Represents the educator/author attributed to news posts."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    bio = models.TextField(
        blank=True,
        help_text="Short biography displayed below each article",
    )
    credentials = models.CharField(
        max_length=200,
        blank=True,
        help_text="e.g. BA English, PGCE, 15+ years teaching experience",
    )
    photo = models.ImageField(
        upload_to="news/authors/",
        null=True,
        blank=True,
        storage=public_storage,
        help_text="Author headshot displayed in the bio card",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("news:category", kwargs={"slug": self.slug})


class Post(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
    ]
    AD_TYPE_CHOICES = [
        ("none", "No Advertisement"),
        ("adsense", "Google AdSense"),
        ("banner", "Banner Image"),
    ]
    RESOURCE_TYPES = [
        ("none", "No Resource"),
        ("pdf", "PDF Document"),
        ("worksheet", "Worksheet"),
        ("guide", "Guide"),
        ("other", "Other Resource"),
    ]

    # Basic fields
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = HTMLField("Content")
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    author = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
        help_text="The educator/author of this article",
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")

    # Dates
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    publish_date = models.DateTimeField(null=True, blank=True)

    # Media fields
    image = models.ImageField(
        upload_to="news/images/", null=True, blank=True, storage=public_storage
    )
    external_image_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="External URL for product image (jpg/png only)",
    )
    youtube_url = models.URLField(blank=True, null=True)

    resource_type = models.CharField(
        max_length=20, choices=RESOURCE_TYPES, default="none"
    )
    thumbnail = models.ImageField(
        upload_to="news/thumbnails/", null=True, blank=True, storage=public_storage
    )
    resource = models.FileField(upload_to="news/resources/", null=True, blank=True)

    resource_title = models.CharField(
        max_length=200, blank=True, help_text="Name of the downloadable resource"
    )

    def get_resource_url(self):
        if self.resource:
            return self.resource.url
        return None

    def get_image_url(self):
        """Get the URL for the main image"""
        try:
            if self.external_image_url:
                return self.external_image_url
            if self.image:
                return self.image.url
            return None
        except Exception:
            return None

    def get_ad_image_url(self):
        """Get the URL for the advertisement image"""
        try:
            if self.ad_image:
                return self.ad_image.url.replace("/media/public/", "/media/")
            return None
        except Exception:
            return None

    # Advertisement fields
    ad_type = models.CharField(max_length=10, choices=AD_TYPE_CHOICES, default="none")
    ad_code = models.TextField(blank=True)
    ad_image = models.ImageField(
        upload_to="news/ads/", null=True, blank=True, storage=public_storage
    )
    ad_url = models.URLField(blank=True)

    # SEO fields
    meta_title = models.CharField(
        max_length=60, blank=True, help_text="SEO Title (60 characters max)"
    )
    meta_description = models.CharField(
        max_length=160, blank=True, help_text="SEO Description (160 characters max)"
    )
    meta_keywords = models.CharField(
        max_length=255, blank=True, help_text="Comma-separated keywords"
    )

    class Meta:
        ordering = ["-publish_date", "-created"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("news:detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        # Auto-set publish date when status changes to published
        if self.status == "published" and not self.publish_date:
            self.publish_date = timezone.now()

        super().save(*args, **kwargs)

    def get_display_image(self):
        """
        Get image URL from uploaded image, thumbnail, or YouTube video thumbnail.
        Order:
        1. Uploaded image
        2. Local thumbnail
        3. YouTube thumbnail (if video URL exists)
        """

        # 1. Uploaded main image
        if self.image:
            return self.image.url

        # 2. Thumbnail (local stored image)
        if self.thumbnail:
            return self.thumbnail.url

        # 3. YouTube video thumbnail
        if self.youtube_url:
            url = self.youtube_url.strip()

            # youtu.be short links
            if "youtu.be" in url:
                video_id = url.split("/")[-1]

            # standard watch?v= links
            elif "watch?v=" in url:
                video_id = url.split("watch?v=")[1].split("&")[0]

            # embed links
            elif "/embed/" in url:
                video_id = url.split("/embed/")[1].split("?")[0]

            # fallback attempt
            else:
                return None

            return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

        # Nothing found
        return None
