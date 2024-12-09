from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from courses.models import Course, Lesson
from news.models import Post
from pages.models import Page

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['home', 'privacy_policy', 'terms_conditions']

    def location(self, item):
        return reverse(item)

class CourseSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Course.objects.filter(status='publish')

    def lastmod(self, obj):
        return obj.updated

class LessonSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Lesson.objects.filter(status='publish', course__status='publish')

    def lastmod(self, obj):
        return obj.updated

class NewsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Post.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated

class PageSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Page.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.publish_date
