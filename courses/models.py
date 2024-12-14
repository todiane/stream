import uuid
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings
from stream.storage import secure_storage, public_storage


class AccessRequirement(models.TextChoices):
    ANYONE = "any", "Anyone"
    EMAIL_REQUIRED = "email", "Email required"


class PublishStatus(models.TextChoices):
    PUBLISHED = "publish", "Published"
    COMING_SOON = "soon", "Coming Soon"
    DRAFT = "draft", "Draft"


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    exam_board = models.CharField(
        max_length=20, choices=[("AQA", "AQA"), ("EDEXCEL", "Edexcel")]
    )

    class Meta:
        verbose_name_plural = "categories"

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
    description = models.TextField(blank=True, null=True)
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
        max_length=10, choices=PublishStatus.choices, default=PublishStatus.DRAFT
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    image = models.ImageField(
        upload_to="courses/images/", null=True, blank=True, storage=public_storage
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

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
    def is_published(self):
        return self.status == PublishStatus.PUBLISHED

    @property
    def is_coming_soon(self):
        return self.status == PublishStatus.COMING_SOON


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    public_id = models.CharField(max_length=130, blank=True, null=True, db_index=True)
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=150, blank=True)
    description = models.TextField(blank=True, null=True)
    thumbnail = models.ImageField(
        upload_to="lessons/thumbnails/", null=True, blank=True, storage=public_storage
    )
    video = models.FileField(
        upload_to="lessons/videos/", null=True, blank=True, storage=public_storage
    )
    youtube_url = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Enter a YouTube URL if you want to embed a video from YouTube.",
    )
    order = models.IntegerField(default=0)
    can_preview = models.BooleanField(
        default=False,
        help_text="If user does not have access to course, can they see this?",
    )
    status = models.CharField(
        max_length=10, choices=PublishStatus.choices, default=PublishStatus.PUBLISHED
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-updated"]
        unique_together = [["course", "slug"]]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            n = 1
            while Lesson.objects.filter(course=self.course, slug=slug).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug

        if not self.public_id:
            self.public_id = generate_public_id(self)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "courses:lesson_detail",
            kwargs={"course_slug": self.course.slug, "lesson_slug": self.slug},
        )

    @property
    def requires_email(self):
        return self.course.access == AccessRequirement.EMAIL_REQUIRED

    def get_display_name(self):
        return f"{self.title} - {self.course.get_display_name()}"

    @property
    def is_coming_soon(self):
        return self.status == PublishStatus.COMING_SOON

    @property
    def has_video(self):
        return self.video is not None or self.youtube_url is not None

    def get_youtube_embed_url(self):
        if self.youtube_url:
            video_id = self.youtube_url.split("v=")[-1]
            return f"https://www.youtube.com/embed/{video_id}"
        return None
