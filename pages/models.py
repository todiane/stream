# pages/models.py
from django.db import models
from django.urls import reverse
from django.utils import timezone
from tinymce.models import HTMLField
from simple_history.models import HistoricalRecords  # type: ignore
from stream.storage import public_storage


class SEOFields(models.Model):
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
        abstract = True


class Hero(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    video_url = models.URLField(
        blank=True,
        help_text="YouTube video URL (e.g., https://www.youtube.com/watch?v=xxxxx)",
    )
    cta_text = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Call to Action Text",
        default="Learn more",
    )
    cta_link = models.CharField(
        max_length=200, blank=True, verbose_name="Call to Action Link"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Hero Section"
        verbose_name_plural = "Hero Section"

    def get_youtube_video_id(self):
        """Extract YouTube video ID from URL."""
        if not self.video_url:  # Changed from youtube_url
            return None

        url = self.video_url  # Changed from youtube_url

        if "youtu.be" in url:
            return url.split("/")[-1].split("?")[0]
        elif "youtube.com/watch?v=" in url:
            return url.split("v=")[1].split("&")[0]
        elif "youtube.com/embed/" in url:
            return url.split("/embed/")[1].split("?")[0]

        return None

    def get_youtube_thumbnail(self):
        """Get YouTube video thumbnail URL."""
        video_id = self.get_youtube_video_id()
        if video_id:
            return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        return None

    def get_youtube_embed_url(self):
        """Get privacy-enhanced YouTube embed URL."""
        video_id = self.get_youtube_video_id()
        if video_id:
            # Use youtube-nocookie.com for GDPR compliance
            return f"https://www.youtube-nocookie.com/embed/{video_id}?rel=0&modestbranding=1"
        return None


class HeroBanner(models.Model):
    text = models.CharField(max_length=200, default="New Videos Available!")
    action_text = models.CharField(max_length=100, default="See what's new")
    action_link = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    badge_text = models.CharField(max_length=50, default="New")

    class Meta:
        verbose_name = "Hero Banner"
        verbose_name_plural = "Hero Banners"

    def __str__(self):
        return self.text


class Page(SEOFields):
    TEMPLATE_CHOICES = (
        ("home", "Homepage"),
        ("about", "About Page"),
        ("tuition", "Tuition Page"),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = HTMLField()
    template = models.CharField(max_length=20, choices=TEMPLATE_CHOICES)
    is_active = models.BooleanField(default=True)
    publish_date = models.DateTimeField(default=timezone.now)
    history = HistoricalRecords()
    second_content = HTMLField(blank=True, null=True)
    third_content = HTMLField(blank=True, null=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.template == "home":
            return reverse("pages:home")
        elif self.template == "about":
            return reverse("pages:about")
        elif self.template == "tuition":
            return reverse("pages:tuition")
        return "/"

    @property
    def is_published(self):
        return self.is_active and self.publish_date <= timezone.now()


class AboutMe(models.Model):
    title = models.CharField(max_length=200, default="About Me")
    description = HTMLField(help_text="Introduction paragraph about yourself")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "About Me Section"
        verbose_name_plural = "About Me Section"


class AboutMeColumns(models.Model):
    title = models.CharField(max_length=200)
    description = HTMLField()
    second_title = models.CharField(max_length=200)
    second_description = HTMLField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "About Me Columns"
        verbose_name_plural = "About Me Columns"


class AboutCourses(models.Model):
    title = models.CharField(max_length=200, default="Take A Look At My Latest Courses")
    description = HTMLField()
    show_courses_section = models.BooleanField(default=True)
    button_text = models.CharField(max_length=50, default="View All Courses")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Courses Section"
        verbose_name_plural = "Courses Section"


class TuitionFeature(models.Model):
    ICON_CHOICES = [
        ("book", "Book"),
        ("pencil", "Pencil"),
        ("star", "Star"),
        ("certificate", "Certificate"),
        ("lightbulb", "Lightbulb"),
        ("laptop", "Laptop"),
        ("people-fill", "People"),
    ]

    SIZE_CHOICES = [
        ("small", "Small"),
        ("large", "Large"),
    ]

    icon = models.CharField(max_length=20, choices=ICON_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    size = models.CharField(max_length=10, choices=SIZE_CHOICES)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Tuition Feature"
        verbose_name_plural = "Tuition Features"

    def __str__(self):
        return self.title


class AboutFeature(models.Model):
    ICON_CHOICES = [
        ("book", "Book"),
        ("pencil", "Pencil"),
        ("star", "Star"),
        ("certificate", "Certificate"),
        ("lightbulb", "Lightbulb"),
        ("laptop", "Laptop"),
        ("people-fill", "People"),
        ("award", "Award"),
        ("journal-text", "Journal"),
    ]

    SIZE_CHOICES = [
        ("small", "Small"),
        ("large", "Large"),
    ]

    icon = models.CharField(max_length=20, choices=ICON_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    size = models.CharField(max_length=10, choices=SIZE_CHOICES)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "About Feature"
        verbose_name_plural = "About Features"

    def __str__(self):
        return self.title


class SiteSettings(models.Model):
    """
    Singleton model for site-wide metadata used in schema markup and SEO.
    Only one record is ever stored (enforced in save()).
    Access via SiteSettings.get() everywhere.
    """

    site_name = models.CharField(max_length=100, default="Stream English")
    site_url = models.URLField(default="https://streamenglish.co.uk")

    # Educator / author
    author_name = models.CharField(
        max_length=100,
        default="Mrs Wear",
        help_text="The educator's display name used in schema and author bios",
    )
    author_credentials = models.CharField(
        max_length=200,
        blank=True,
        help_text="e.g. BA English, PGCE, 15+ years teaching experience",
    )
    author_description = models.TextField(
        blank=True,
        help_text="Short bio for the Person schema (1–2 sentences)",
    )

    # Contact & reach
    contact_email = models.EmailField(
        blank=True,
        help_text="Public contact email surfaced in the Organization schema",
    )
    founding_year = models.CharField(
        max_length=4,
        blank=True,
        help_text="Year the site / organisation was founded (e.g. 2020)",
    )
    area_served = models.CharField(max_length=100, default="United Kingdom")

    # Social channels
    youtube_url = models.URLField(
        blank=True, default="https://www.youtube.com/c/StreamEnglish"
    )
    instagram_url = models.URLField(
        blank=True, default="https://www.instagram.com/streamenglishuk/"
    )
    tiktok_url = models.URLField(
        blank=True, default="https://tiktok.com/streamenglish"
    )
    twitter_url = models.URLField(
        blank=True, default="https://twitter.com/stream_english"
    )

    # Legal & Compliance
    show_digital_withdrawal_consent = models.BooleanField(
        default=False,
        help_text=(
            "Show a required checkbox at checkout asking customers to waive "
            "their EU/UK 14-day digital content withdrawal right."
        ),
        verbose_name="Show digital withdrawal consent checkbox",
    )
    digital_withdrawal_consent_text = models.CharField(
        max_length=500,
        blank=True,
        default=(
            "I agree that by purchasing this digital content, I waive my right "
            "to withdraw from this contract under the Consumer Contracts "
            "Regulations 2013 / EU Consumer Rights Directive once the download "
            "has begun."
        ),
        help_text="Legal text displayed next to the withdrawal consent checkbox at checkout.",
        verbose_name="Digital withdrawal consent text",
    )

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # Enforce singleton — delete any other record before saving
        self.__class__.objects.exclude(pk=self.pk).delete()
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        """Always returns the single SiteSettings record, creating it if absent."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Testimonial(models.Model):
    image = models.ImageField(
        upload_to="testimonials/images/", null=True, blank=True, storage=public_storage
    )
    external_image_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="External URL for testimonial image (jpg/png only)",
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"

    def get_image_url(self):
        """Get the URL for the testimonial image"""
        try:
            if self.external_image_url:
                return self.external_image_url
            if self.image:
                return self.image.url
            return None
        except Exception:
            return None
