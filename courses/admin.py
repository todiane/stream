# courses/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Course, Lesson, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "exam_board", "slug"]
    list_filter = ["exam_board"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}


class LessonInline(admin.StackedInline):
    model = Lesson
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = [
        "public_id",
        "updated",
        "display_thumbnail",
        "display_video",
    ]
    extra = 0

    def display_thumbnail(self, obj):
        thumbnail_url = obj.get_thumbnail_url()
        if thumbnail_url:
            return format_html(
                '<img src="{}" width="200" class="admin-thumbnail" style="border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);" />',
                thumbnail_url,
            )
        return "No thumbnail uploaded"

    def display_video(self, obj):
        video_url = obj.get_video_url()
        if video_url:
            return format_html(
                '<video width="550" controls class="admin-video" style="border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);"><source src="{}"></video>',
                video_url,
            )
        elif obj.youtube_url:
            embed_url = obj.get_youtube_embed_url()
            return format_html(
                '<div class="admin-youtube" style="margin: 10px 0;">'
                '<iframe width="550" height="315" src="{}" frameborder="0" '
                'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
                "allowfullscreen></iframe><br>"
                '<a href="{}" target="_blank" class="youtube-link">View on YouTube</a>'
                "</div>",
                embed_url,
                obj.youtube_url,
            )
        return "No video available"

    display_thumbnail.short_description = "Thumbnail Preview"
    display_video.short_description = "Video Preview"


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = [
        "title",
        "category",
        "status",
        "access",
        "public_id",
        "display_thumbnail",
    ]
    list_filter = ["status", "access", "category", "category__exam_board"]
    fields = [
        "public_id",
        "title",
        "slug",
        "description",
        "category",
        "status",
        "image",
        "access",
        "display_image",
    ]
    readonly_fields = ["public_id", "display_image"]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ["title", "description", "category__name", "slug"]

    def display_image(self, obj):
        image_url = obj.get_image_url()
        if image_url:
            return format_html(
                '<img src="{}" width="200" class="admin-image" style="border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);" />',
                image_url,
            )
        return "No image uploaded"

    def display_thumbnail(self, obj):
        image_url = obj.get_thumbnail_url()
        if image_url:
            return format_html(
                '<img src="{}" width="50" class="admin-thumbnail" style="border-radius: 3px;" />',
                image_url,
            )
        return "-"

    display_image.short_description = "Current Image"
    display_thumbnail.short_description = "Thumbnail"

    class Media:
        css = {"all": ["admin/css/custom_admin.css"]}
