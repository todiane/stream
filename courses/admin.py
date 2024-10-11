from django.contrib import admin
from django.utils.html import format_html
from .models import Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'access']
    fields = ['title', 'description', 'image', 'status', 'access', 'display_image']
    list_filter = ['status', 'access']
    search_fields = ['title', 'description']
    readonly_fields = ['display_image']

    def display_image(self, obj):
        if obj.image:
            return format_html(f"<img src='{obj.image.url}' width='500' />")
        return "No image"

    display_image.short_description = 'Current Image'