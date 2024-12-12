from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from courses.models import Course, Lesson
from shop.models import Product

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=False)
    bio = models.TextField(max_length=500, blank=True)
    enrolled_courses = models.ManyToManyField(Course, blank=True, related_name='enrolled_students')
    watched_videos = models.ManyToManyField(Lesson, blank=True, related_name='watched_by')
    last_watched_lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='last_watched_by')
    email_subscribed = models.BooleanField(default=True) # For marketing/notification emails
    email_verified = models.BooleanField(default=False)  # For email verification status
    purchased_products = models.ManyToManyField('shop.Product', blank=True, related_name='purchasers')

    def __str__(self):
        return f"{self.user.username}'s profile"

    def get_watched_videos_count(self):
        return self.watched_videos.count()

    def get_courses_completion_percentage(self):
        enrolled_courses = self.enrolled_courses.all()
        if not enrolled_courses:
            return 0
        
        total_progress = sum(self.get_course_completion_percentage(course) 
                            for course in enrolled_courses)
        return total_progress / enrolled_courses.count()

    def is_course_completed(self, course):
        total_lessons = course.lesson_set.count()
        watched_lessons = self.watched_videos.filter(course=course).count()
        return total_lessons > 0 and watched_lessons == total_lessons

    def get_course_completion_percentage(self, course):
        total_lessons = course.lesson_set.count()
        if total_lessons == 0:
            return 0
        watched_lessons = self.watched_videos.filter(course=course).count()
        return (watched_lessons / total_lessons) * 100

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        try:
            instance.profile.save()
        except Profile.DoesNotExist:
            Profile.objects.create(user=instance)


class ContactSubmission(models.Model):
    REASON_CHOICES = [
        ('general', 'General Inquiry'),
        ('tuition', 'Tuition Inquiry'),
        ('technical', 'Technical Support'),
        ('other', 'Other')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Parent/Guardian details (for tuition inquiries)
    parent_first_name = models.CharField(max_length=50, blank=True, null=True)
    parent_last_name = models.CharField(max_length=50, blank=True, null=True)
    parent_email = models.EmailField(blank=True, null=True)
    parent_phone = models.CharField(max_length=20, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_reason_display()} from {self.user.username}"
