from django.db import models
from django.urls import reverse
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field
from simple_history.models import HistoricalRecords
from cloudinary.models import CloudinaryField
from helpers._cloudinary import get_cloudinary_image_object, cloudinary_init

class SEOFields(models.Model):
    meta_title = models.CharField(max_length=60, blank=True, help_text="SEO Title (60 characters max)")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO Description (160 characters max)")
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="Comma-separated keywords")

    class Meta:
        abstract = True

class Hero(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    video_url = models.URLField(
        blank=True, 
        help_text="YouTube video URL (e.g., https://www.youtube.com/watch?v=xxxxx)"
    )
    cta_text = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name="Call to Action Text",
        default="Learn more"
    )
    cta_link = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name="Call to Action Link"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Hero Section"
        verbose_name_plural = "Hero Section"


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
        ('home', 'Homepage'),
        ('about', 'About Page'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = CKEditor5Field()
    template = models.CharField(max_length=20, choices=TEMPLATE_CHOICES)
    is_active = models.BooleanField(default=True)
    publish_date = models.DateTimeField(default=timezone.now)
    history = HistoricalRecords()

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.template == 'home':
            return reverse('pages:home')
        return reverse('pages:page_detail', kwargs={'slug': self.slug})

    @property
    def is_published(self):
        return self.is_active and self.publish_date <= timezone.now()

class AboutMe(models.Model):
    title = models.CharField(max_length=200, default="About Me")
    subtitle = models.CharField(max_length=200, help_text="e.g., 'Helping Students achieve Grade 9'")
    description = models.TextField(help_text="Introduction paragraph about yourself")
    qualifications = models.TextField(help_text="List of qualifications - stored as plain text")
    image = CloudinaryField(
        "image",
        null=True,
        folder="about",
        resource_type="image",
        transformation={"quality": "auto:eco"},
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "About Me Section"
        verbose_name_plural = "About Me Section"

    def get_image_url(self):
        return get_cloudinary_image_object(self, 'image')

class AboutTuition(models.Model):
    title = models.CharField(max_length=200, default="Tuition Lessons")
    description = CKEditor5Field()
    booking_title = models.CharField(max_length=200, default="Book Your Session")
    booking_description = CKEditor5Field()
    booking_button_text = models.CharField(max_length=50, default="Book HERE!")
    booking_button_url = models.CharField(max_length=200, default="/booking-form/")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tuition Information"
        verbose_name_plural = "Tuition Information"

class AboutCourses(models.Model):
    title = models.CharField(max_length=200, default="Take A Look At My Latest Courses")
    description = CKEditor5Field()
    show_courses_section = models.BooleanField(default=True)
    button_text = models.CharField(max_length=50, default="View All Courses")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Courses Section"
        verbose_name_plural = "Courses Section"
