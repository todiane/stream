# news/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django import forms

from .models import Author, Category, Post
from .widgets import ImageFileInput


# -----------------------------
# AUTHOR ADMIN
# -----------------------------
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["name", "credentials"]
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("name", "slug", "credentials")}),
        ("Bio & Photo", {"fields": ("bio", "photo")}),
    )


# -----------------------------
# CATEGORY ADMIN
# -----------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


# -----------------------------
# POST ADMIN FORM (adds webp support)
# -----------------------------
class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = "__all__"
        widgets = {
            "image": ImageFileInput,
            "thumbnail": ImageFileInput,
            "ad_image": ImageFileInput,
        }


# -----------------------------
# POST ADMIN
# -----------------------------
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm

    list_display = [
        "title",
        "content_type",
        "category",
        "status",
        "publish_date",
        "display_thumbnail",
    ]

    list_filter = ["status", "content_type", "category", "created", "publish_date"]
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
                    "content_type",
                    "category",
                    "author",
                    "content",
                    "status",
                    "publish_date",
                )
            },
        ),
        (
            "Media",
            {
                "fields": (
                    "image",
                    "external_image_url",
                    "youtube_url",
                    "thumbnail",
                    "display_media",
                ),
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

    # -----------------------------
    # THUMBNAIL DISPLAY
    # -----------------------------
    def display_thumbnail(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" width="50" />', obj.thumbnail.url)
        if obj.image:
            return format_html('<img src="{}" width="50" />', obj.image.url)
        return "-"

    display_thumbnail.short_description = "Thumbnail"

    # -----------------------------
    # MEDIA DISPLAY (image + YouTube)
    # -----------------------------
    def display_media(self, obj):
        html = []

        image_url = obj.get_image_url()
        youtube_url = (
            obj.get_youtube_embed_url()
            if hasattr(obj, "get_youtube_embed_url")
            else None
        )

        if image_url:
            html.append(
                f'<div class="mb-4">'
                f"<strong>Image:</strong><br>"
                f'<img src="{image_url}" width="200" />'
                f"</div>"
            )

        if youtube_url:
            html.append(
                f'<div class="mb-4">'
                f"<strong>YouTube Video:</strong><br>"
                f'<iframe width="400" height="225" src="{youtube_url}" '
                f'frameborder="0" allowfullscreen></iframe>'
                f"</div>"
            )

        return mark_safe("".join(html)) if html else "-"

    # -----------------------------
    # SAVE WITH EXTERNAL URL CLEANING
    # -----------------------------
    def save_model(self, request, obj, form, change):
        if "external_image_url" in form.changed_data:
            if hasattr(self, "clean_external_image_url"):
                obj.external_image_url = self.clean_external_image_url(
                    obj.external_image_url
                )
        super().save_model(request, obj, form, change)
