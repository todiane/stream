from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django import forms
from simple_history.admin import SimpleHistoryAdmin  # type: ignore
from .models import (
    AboutFeature,
    Page,
    Hero,
    HeroBanner,
    AboutMe,
    AboutCourses,
    TuitionFeature,
    Testimonial,
)
from stream.utils import sanitize_text


class PageAdminForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        # Clean text fields
        text_fields = ["title", "meta_title", "meta_description", "meta_keywords"]
        for field in text_fields:
            if cleaned_data.get(field):
                cleaned_data[field] = sanitize_text(cleaned_data[field])
        return cleaned_data


@admin.register(Page)
class PageAdmin(SimpleHistoryAdmin):
    form = PageAdminForm
    list_display = ["title", "template", "is_active", "publish_date", "preview_link"]
    list_filter = ["is_active", "template"]
    search_fields = ["title", "content", "meta_title", "meta_description"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["preview_link"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "template",
                    "content",
                    "second_content",
                    "third_content",
                )
            },
        ),
        ("Publishing", {"fields": ("is_active", "publish_date")}),
        (
            "SEO",
            {
                "fields": ("meta_title", "meta_description", "meta_keywords"),
                "classes": ("collapse",),
            },
        ),
    )

    def preview_link(self, obj):
        if obj.pk:
            url = reverse("pages:preview", kwargs={"pk": obj.pk})
            return format_html(
                '<a href="{}" target="_blank" class="button">Preview</a>', url
            )
        return "Save first to preview"

    preview_link.short_description = "Preview"

    def save_model(self, request, obj, form, change):
        # Sanitize text fields before saving
        obj.title = sanitize_text(obj.title)
        if obj.meta_title:
            obj.meta_title = sanitize_text(obj.meta_title)
        if obj.meta_description:
            obj.meta_description = sanitize_text(obj.meta_description)
        if obj.meta_keywords:
            obj.meta_keywords = sanitize_text(obj.meta_keywords)

        # Ensure only one homepage exists
        if obj.template == "home":
            Page.objects.filter(template="home").exclude(pk=obj.pk).update(
                template="about"
            )
        super().save_model(request, obj, form, change)


@admin.register(Hero)
class HeroAdmin(SimpleHistoryAdmin):
    list_display = ["title", "is_active"]
    search_fields = ["title", "description"]

    fieldsets = (
        (None, {"fields": ("title", "subtitle", "description", "is_active")}),
        (
            "Video",
            {
                "fields": ("video_url",),
                "description": "Add a YouTube video URL to display in the hero section",
            },
        ),
        ("Call to Action", {"fields": ("cta_text", "cta_link")}),
    )

    def save_model(self, request, obj, form, change):
        obj.title = sanitize_text(obj.title)
        if obj.subtitle:
            obj.subtitle = sanitize_text(obj.subtitle)
        if obj.description:
            obj.description = sanitize_text(obj.description)

        if obj.is_active:
            Hero.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)


@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = ["text", "is_active"]

    def save_model(self, request, obj, form, change):
        obj.text = sanitize_text(obj.text)
        if obj.is_active:
            HeroBanner.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)


@admin.register(AboutMe)
class AboutMeAdmin(admin.ModelAdmin):
    list_display = ["title", "is_active"]
    fields = ["title", "description", "is_active"]

    def save_model(self, request, obj, form, change):
        obj.title = sanitize_text(obj.title)
        if obj.is_active:
            AboutMe.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)


@admin.register(AboutFeature)
class AboutFeatureAdmin(admin.ModelAdmin):
    list_display = ["title", "icon", "size", "order", "is_active"]
    list_filter = ["is_active", "size"]
    search_fields = ["title", "description"]
    ordering = ["order"]
    list_editable = ["order", "is_active"]

    def save_model(self, request, obj, form, change):
        obj.title = sanitize_text(obj.title)
        if obj.description:
            obj.description = sanitize_text(obj.description)
        super().save_model(request, obj, form, change)


@admin.register(AboutCourses)
class AboutCoursesAdmin(admin.ModelAdmin):
    list_display = ["title", "show_courses_section", "is_active"]
    fields = [
        "title",
        "description",
        "show_courses_section",
        "button_text",
        "is_active",
    ]

    def save_model(self, request, obj, form, change):
        obj.title = sanitize_text(obj.title)
        if obj.description:
            obj.description = sanitize_text(obj.description)
        if obj.button_text:
            obj.button_text = sanitize_text(obj.button_text)

        if obj.is_active:
            AboutCourses.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)


@admin.register(TuitionFeature)
class TuitionFeatureAdmin(admin.ModelAdmin):
    list_display = ["title", "icon", "size", "order", "is_active"]
    list_filter = ["is_active", "size"]
    search_fields = ["title", "description"]
    ordering = ["order"]
    list_editable = ["order", "is_active"]

    def save_model(self, request, obj, form, change):
        obj.title = sanitize_text(obj.title)
        if obj.description:
            obj.description = sanitize_text(obj.description)
        super().save_model(request, obj, form, change)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ["id", "preview_image", "order", "is_active"]
    list_editable = ["order", "is_active"]
    ordering = ["order"]

    def preview_image(self, obj):
        image_url = obj.get_image_url()
        if image_url:
            return format_html('<img src="{}" style="max-height: 50px;" />', image_url)
        return "No image"

    preview_image.short_description = "Image Preview"
