from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from courses.models import Course, Lesson

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=False)
    bio = models.TextField(max_length=500, blank=True)
    enrolled_courses = models.ManyToManyField(Course, blank=True, related_name='enrolled_students')
    watched_videos = models.ManyToManyField(Lesson, blank=True, related_name='watched_by')
    last_watched_lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='last_watched_by')

    def __str__(self):
        return f"{self.user.username}'s profile"

    def get_watched_videos_count(self):
        return self.watched_videos.count()

    def get_courses_completion_percentage(self):
        total_courses = self.enrolled_courses.count()
        if total_courses == 0:
            return 0
        completed_courses = sum(1 for course in self.enrolled_courses.all() if self.is_course_completed(course))
        return (completed_courses / total_courses) * 100

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
    instance.profile.save()