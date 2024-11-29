import uuid
from django.db import models
from django.utils.text import slugify
from cloudinary.models import CloudinaryField
from django.conf import settings
import cloudinary
from helpers._cloudinary import get_cloudinary_image_object, cloudinary_init

cloudinary_init()

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
        max_length=20,
        choices=[
            ('AQA', 'AQA'),
            ('EDEXCEL', 'Edexcel')
        ]
    )
    
    class Meta:
        verbose_name_plural = 'categories'
        
    def __str__(self):
        return f"{self.name} ({self.exam_board})"

def handle_upload(instance, filename):
    return f"{filename}"

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
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses', null=True, blank=True)
    public_id = models.CharField(max_length=130, blank=True, null=True, db_index=True)
    access = models.CharField(max_length=5, choices=AccessRequirement.choices, default=AccessRequirement.EMAIL_REQUIRED)
    status = models.CharField(max_length=10, choices=PublishStatus.choices, default=PublishStatus.DRAFT)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    image = CloudinaryField(
        "image", 
        null=True,
        folder="courses",  
        resource_type="auto",  # Add this line to handle different file types
        allowed_formats=['jpg', 'jpeg', 'png', 'svg', 'webp', 'gif'],
        transformation={"quality": "auto:eco"},
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            try:
                public_id = self.image.public_id
                print(f"Uploading image with public_id: {public_id}")
            except AttributeError:
                print("Image has not been uploaded yet, no public_id available.")
        print(f"Using cloud name: {settings.CLOUDINARY_STORAGE['CLOUD_NAME']}")

    def get_absolute_url(self):
        return self.path
    
    @property
    def path(self):
        return f"/courses/{self.public_id}"

    def get_display_name(self):
        return f"{self.title} - Course"

    def get_image_url(self):
        return get_cloudinary_image_object(self, 'image')

    def clear_image(self):
        if self.image:
            try:
                public_id = self.image.public_id
                cloudinary.uploader.destroy(public_id)
                self.image = None
                self.save()
                return True
            except Exception as e:
                print(f"Error clearing course image: {e}")
                return False
        return False

    def get_thumbnail(self):
        if not self.image:
            return settings.DEFAULT_PLACEHOLDER_IMAGE
        return get_cloudinary_image_object(
            self, 
            field_name='image',
            width=382,
            as_html=False
        )

    def get_display_image(self):
        if not self.image:
            return settings.DEFAULT_PLACEHOLDER_IMAGE
        return get_cloudinary_image_object(
            self, 
            field_name='image',
            width=750,
            as_html=False
        )

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
    description = models.TextField(blank=True, null=True)
    thumbnail = CloudinaryField(
        "image",
        blank=True, 
        null=True,
        folder="lessons",
        resource_type="image",
        allowed_formats=['jpg', 'jpeg', 'png', 'svg', 'webp', 'gif'],
        transformation={"quality": "auto:eco"},
    )
    video = CloudinaryField(
        "video",
        blank=True, 
        null=True,
        folder="lessons",
        resource_type="video",
        type='private',
    )
    youtube_url = models.URLField(
        max_length=200, 
        blank=True, 
        null=True, 
        help_text="Enter a YouTube URL if you want to embed a video from YouTube."
    )
    order = models.IntegerField(default=0)
    can_preview = models.BooleanField(default=False, help_text="If user does not have access to course, can they see this?")
    status = models.CharField(max_length=10, choices=PublishStatus.choices, default=PublishStatus.PUBLISHED)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-updated']

    def save(self, *args, **kwargs):
        if self.public_id == "" or self.public_id is None:
            self.public_id = generate_public_id(self)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return self.path

    @property
    def path(self):
        course_path = self.course.path
        if course_path.endswith("/"):
            course_path = course_path[:-1]
        return f"{course_path}/lessons/{self.public_id}"

    def get_thumbnail_url(self):
        return get_cloudinary_image_object(self, 'thumbnail')

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
    
    def get_thumbnail(self):
        width = 382
        if self.thumbnail:
            return get_cloudinary_image_object(
                self,
                field_name='thumbnail',
                format='jpg',
                width=width,
                as_html=False
            )
        elif self.video:
            return get_cloudinary_image_object(
                self, 
                field_name='video',
                format='jpg',
                width=width,
                as_html=False
            )
        return settings.DEFAULT_PLACEHOLDER_IMAGE

    def get_display_image(self):
        if self.youtube_url:
            video_id = self.youtube_url.split('v=')[-1]
            return f"https://www.youtube.com/embed/{video_id}"
        elif self.video:
            return get_cloudinary_image_object(self, field_name='video')
        return None
    