# courses/models.py

import json
import re
import uuid
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from stream.storage import public_storage
from tinymce.models import HTMLField  # type: ignore
from django.core.exceptions import ValidationError
from .utils import sanitize_text
from stream.utils import custom_slugify


# Define choices as module-level constants
PUBLISH_STATUS_CHOICES = [
    ("publish", "Published"),
    ("soon", "Coming Soon"),
    ("draft", "Draft"),
]


class AccessRequirement(models.TextChoices):
    ANYONE = "any", "Anyone"
    EMAIL_REQUIRED = "email", "Email required"


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    exam_board = models.CharField(
        max_length=20,
        choices=[("AQA", "AQA"), ("EDEXCEL", "Edexcel"), ("BOTH", "Both Exam Boards")],
    )

    class Meta:
        verbose_name_plural = "categories"

    def clean(self):
        # Sanitize the name and description before validation
        if self.name:
            sanitized_name = sanitize_text(self.name)
            if sanitized_name != self.name:
                self.name = sanitized_name

        if self.description:
            sanitized_description = sanitize_text(self.description)
            if sanitized_description != self.description:
                self.description = sanitized_description

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.exam_board})"


def generate_public_id(instance, *args, **kwargs):
    title = instance.title
    unique_id = str(uuid.uuid4()).replace("-", "")
    if not title:
        return unique_id
    slug = slugify(title)
    unique_id_short = unique_id[:5]
    return f"{slug}-{unique_id_short}"


class Course(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, null=True, blank=True)
    description = HTMLField(blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="courses",
        null=True,
        blank=True,
    )
    public_id = models.CharField(max_length=130, blank=True, null=True, db_index=True)
    access = models.CharField(
        max_length=5,
        choices=AccessRequirement.choices,
        default=AccessRequirement.EMAIL_REQUIRED,
    )
    status = models.CharField(
        max_length=10, choices=PUBLISH_STATUS_CHOICES, default="draft"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    order = models.IntegerField(default=0)
    external_image_url = models.URLField(
        blank=True,
        null=True,
        help_text="External URL for the course image (must be jpg or png)",
    )
    image = models.ImageField(
        upload_to="courses/images/", null=True, blank=True, storage=public_storage
    )

    class Meta:
        ordering = ["order", "-updated"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = custom_slugify(self.title)
        if not self.public_id:
            self.public_id = generate_public_id(self)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return self.path

    @property
    def path(self):
        return reverse("courses:course_detail", kwargs={"course_slug": self.slug})

    def get_display_name(self):
        return f"{self.title} - Course"

    @property
    def get_display_image(self):
        """Get image URL from either uploaded image or external URL"""
        return self.get_image_url()

    def get_image_url(self):
        """Get the URL for the main image"""
        try:
            if self.external_image_url:
                return self.external_image_url
            return self.image.url if self.image else None
        except Exception:
            return None

    def get_thumbnail_url(self):
        """Use main image as thumbnail"""
        return self.get_image_url()

    @property
    def is_published(self):
        return self.status == "publish"

    @property
    def is_coming_soon(self):
        return self.status == "soon"


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    public_id = models.CharField(max_length=130, blank=True, null=True, db_index=True)
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=150, blank=True)
    description = HTMLField(blank=True, null=True)
    thumbnail = models.ImageField(
        upload_to="lessons/thumbnails/", null=True, blank=True, storage=public_storage
    )
    # Note: video field kept for backwards compatibility but no longer used
    video = models.FileField(
        upload_to="lessons/videos/", null=True, blank=True, storage=public_storage
    )
    youtube_url = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Enter a YouTube URL if you want to embed a video from YouTube.",
    )
    duration_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=(
            "Video length in seconds, used for the SEO video schema. "
            "E.g. a 40-minute video = 2400. Leave blank if unknown."
        ),
    )
    external_image_url = models.URLField(
        blank=True,
        null=True,
        help_text="External URL for the lesson thumbnail (must be jpg or png)",
    )
    order = models.IntegerField(default=0)
    can_preview = models.BooleanField(
        default=False,
        help_text="If user does not have access to course, can they see this?",
    )
    status = models.CharField(
        max_length=10, choices=PUBLISH_STATUS_CHOICES, default="publish"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-updated"]
        unique_together = [["course", "slug"]]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = custom_slugify(self.title)
            slug = base_slug
            n = 1
            while Lesson.objects.filter(course=self.course, slug=slug).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug

        if not self.public_id:
            self.public_id = generate_public_id(self)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            "courses:lesson_detail",
            kwargs={"course_slug": self.course.slug, "lesson_slug": self.slug},
        )

    @property
    def has_video(self):
        """Check if lesson has a YouTube video."""
        return bool(self.youtube_url)

    def get_video_id(self):
        """Extract YouTube video ID from URL."""
        if not self.youtube_url:
            return None

        url = self.youtube_url

        # Handle different YouTube URL formats
        if "youtube.com/watch?v=" in url:
            return url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            return url.split("/")[-1].split("?")[0]
        elif "youtube.com/embed/" in url:
            return url.split("/embed/")[1].split("?")[0]

        return None

    def get_youtube_embed_url(self):
        """Get privacy-enhanced YouTube embed URL."""
        video_id = self.get_video_id()
        if video_id:
            return f"https://www.youtube-nocookie.com/embed/{video_id}"
        return None

    def get_thumbnail_url(self):
        """
        Get thumbnail URL with fallbacks:
        1. External image URL
        2. Uploaded thumbnail
        3. YouTube video thumbnail
        """
        try:
            if self.external_image_url:
                return self.external_image_url
            if self.thumbnail:
                return self.thumbnail.url

            # Fall back to YouTube thumbnail
            video_id = self.get_video_id()
            if video_id:
                return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

            return None
        except Exception:
            return None

    def get_iso_duration(self):
        """Return the video length as an ISO 8601 duration (e.g. PT40M30S).

        Returns None when the duration is unknown so the schema can omit it
        rather than publish a misleading value.
        """
        if not self.duration_seconds:
            return None
        total = int(self.duration_seconds)
        hours, remainder = divmod(total, 3600)
        minutes, seconds = divmod(remainder, 60)
        iso = "PT"
        if hours:
            iso += f"{hours}H"
        if minutes:
            iso += f"{minutes}M"
        if seconds:
            iso += f"{seconds}S"
        return iso if iso != "PT" else None

    def get_video_schema(self):
        """Return a VALID JSON-LD VideoObject string for SEO and E-E-A-T.

        Previously this returned a Python dict that the template rendered with
        its repr (single quotes / None), producing invalid JSON-LD that search
        engines could not parse. It now returns a proper JSON string and
        attributes the video to the organisation and the named educator.
        """
        video_id = self.get_video_id()
        if not video_id:
            return ""

        site_url = "https://streamenglish.co.uk"

        clean_description = ""
        if self.description:
            clean_description = re.sub(r"<[^>]+>", "", self.description).strip()

        schema = {
            "@context": "https://schema.org",
            "@type": "VideoObject",
            "name": self.title,
            "description": clean_description[:300] if clean_description else self.title,
            "thumbnailUrl": self.get_thumbnail_url(),
            "uploadDate": self.timestamp.strftime("%Y-%m-%d"),
            "contentUrl": self.youtube_url,
            "embedUrl": self.get_youtube_embed_url(),
            "duration": self.get_iso_duration(),
            "inLanguage": "en-GB",
            "isFamilyFriendly": True,
            "learningResourceType": "Video lesson",
            "educationalLevel": "GCSE",
            "publisher": {
                "@type": "EducationalOrganization",
                "@id": f"{site_url}/#organization",
                "name": "Stream English",
            },
            "author": {
                "@type": "Person",
                "@id": f"{site_url}/#educator",
                "name": "Mrs Wear",
            },
        }

        # Drop empty values so we never emit null/empty fields.
        schema = {k: v for k, v in schema.items() if v not in (None, "", [])}

        # Escape any closing tags inside JSON to keep the <script> block safe.
        return json.dumps(schema).replace("</", "<\\/")

    @property
    def requires_email(self):
        return self.course.access == AccessRequirement.EMAIL_REQUIRED

    def get_display_name(self):
        return f"{self.title} - {self.course.get_display_name()}"

    @property
    def is_coming_soon(self):
        return self.status == "soon"
