# courses/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.core.exceptions import ValidationError
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
        "display_youtube_preview",
    ]
    fields = [
        "title",
        "slug",
        "description",
        "youtube_url",
        "thumbnail",
        "external_image_url",
        "order",
        "can_preview",
        "status",
        "display_thumbnail",
        "display_youtube_preview",
    ]
    extra = 0

    def display_thumbnail(self, obj):
        """Display the lesson thumbnail in admin."""
        thumbnail_url = obj.get_thumbnail_url()
        if thumbnail_url:
            return format_html(
                '<img src="{}" width="200" style="border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                thumbnail_url,
            )
        return "No thumbnail"

    display_thumbnail.short_description = "Thumbnail Preview"

    def display_youtube_preview(self, obj):
        """Display YouTube video preview in admin."""
        video_id = obj.get_video_id()
        if video_id:
            return format_html(
                """
                <div style="max-width: 400px;">
                    <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <iframe 
                            src="https://www.youtube-nocookie.com/embed/{}" 
                            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                            allowfullscreen>
                        </iframe>
                    </div>
                    <p style="margin-top: 8px; color: #666; font-size: 12px;">
                        Video ID: {} | 
                        <a href="https://www.youtube.com/watch?v={}" target="_blank">View on YouTube ↗</a>
                    </p>
                </div>
                """,
                video_id,
                video_id,
                video_id,
            )
        return "No YouTube video - Add a YouTube URL above"

    display_youtube_preview.short_description = "Video Preview"


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
        "order",
    ]
    list_filter = ["status", "access", "category", "category__exam_board"]
    search_fields = ["title", "description", "category__name", "slug"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["public_id", "display_image"]
    list_editable = ["order"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "public_id",
                    "title",
                    "slug",
                    "description",
                    "category",
                    "status",
                    "access",
                    "order",
                )
            },
        ),
        (
            "Media",
            {
                "fields": ("image", "external_image_url", "display_image"),
                "classes": ("collapse",),
            },
        ),
    )

    def clean_external_image_url(self, value):
        if value and not any(
            value.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png"]
        ):
            raise ValidationError("External image URL must point to a JPG or PNG file")
        return value

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
