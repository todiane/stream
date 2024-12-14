# courses/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Course, Lesson, Category
import django_ckeditor_5.widgets


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
        "display_image",
        "display_video",
    ]
    extra = 0

    def display_image(self, obj):
        if obj.image:
            return format_html(f'<img src="{obj.image.url}" width="200" />')
        return "-"

    def display_video(self, obj):
        if obj.video:
            return format_html(
                f'<video width="550" controls><source src="{obj.video.url}"></video>'
            )
        return "-"

    def display_thumbnail(self, obj):
        if obj.thumbnail:
            return format_html(f'<img src="{obj.thumbnail.url}" width="50" />')
        return "-"


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ["title", "category", "status", "access", "public_id"]
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

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == "description":
            kwargs["widget"] = django_ckeditor_5.widgets.CKEditor5Widget(
                config_name="default", attrs={"class": "django_ckeditor_5"}
            )
        return super().formfield_for_dbfield(db_field, **kwargs)

    def display_image(self, obj):
        if obj.image:
            return format_html(f'<img src="{obj.image.url}" width="200" />')
        return "-"

    display_image.short_description = "Current Image"
