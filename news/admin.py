# news/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "status", "publish_date", "display_thumbnail"]
    list_filter = ["status", "category", "created", "publish_date"]
    search_fields = ["title", "content", "meta_title", "meta_description"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "publish_date"
    readonly_fields = ["display_media"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "category",
                    "content",
                    "status",
                    "publish_date",
                ),
            },
        ),
        (
            "Media",
            {
                "fields": ("image", "youtube_url", "thumbnail", "display_media"),
                "classes": ("collapse",),
            },
        ),
        (
            "Advertisement",
            {
                "fields": ("ad_type", "ad_code", "ad_image", "ad_url"),
                "classes": ("collapse",),
            },
        ),
        (
            "Resource",
            {
                "fields": ("resource_type", "resource_title", "resource"),
                "classes": ("collapse",),
            },
        ),
        (
            "SEO",
            {
                "fields": ("meta_title", "meta_description", "meta_keywords"),
                "classes": ("collapse",),
            },
        ),
    )

    def display_media(self, obj):
        html = []

        if obj.image:
            html.append(
                f'<div class="mb-4">'
                f"<strong>Image:</strong><br/>"
                f'<img src="{obj.image.url}" width="200" />'
                f"</div>"
            )

        if obj.youtube_url:
            html.append(
                f'<div class="mb-4">'
                f"<strong>YouTube URL:</strong><br/>"
                f"{obj.youtube_url}"
                f"</div>"
            )

        if obj.resource and obj.resource_type != "none":
            html.append(
                f'<div class="mb-4">'
                f"<strong>Resource:</strong><br/>"
                f"Type: {obj.get_resource_type_display()}<br/>"
                f"Title: {obj.resource_title}<br/>"
                f'<a href="{obj.get_resource_url()}" target="_blank">'
                f"Download Resource</a></div>"
            )

        return format_html("".join(html)) if html else "-"

    display_media.short_description = "Media Preview"

    def display_thumbnail(self, obj):
        if obj.thumbnail:
            return format_html(f'<img src="{obj.thumbnail.url}" width="50" />')
        return "-"

    display_thumbnail.short_description = "Thumbnail"
