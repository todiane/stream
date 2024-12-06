from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin
from .models import Page, Hero, HeroBanner, AboutMe, AboutTuition, AboutCourses


@admin.register(Hero)
class HeroAdmin(SimpleHistoryAdmin):
    list_display = ['title', 'is_active']
    search_fields = ['title', 'description']
    fieldsets = (
        (None, {
            'fields': ('title', 'subtitle', 'description', 'is_active')
        }),
        ('Video', {
            'fields': ('video_url',),
            'description': 'Add a YouTube video URL to display in the hero section'
        }),
        ('Call to Action', {
            'fields': ('cta_text', 'cta_link')
        })
    )

    def save_model(self, request, obj, form, change):
        # Ensure only one hero section is active
        if obj.is_active:
            Hero.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)


@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = ['text', 'is_active']
    
    def save_model(self, request, obj, form, change):
        if obj.is_active:
            HeroBanner.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)


@admin.register(Page)
class PageAdmin(SimpleHistoryAdmin):
    list_display = ['title', 'template', 'is_active', 'publish_date', 'preview_link']
    list_filter = ['is_active', 'template']
    search_fields = ['title', 'content', 'meta_title', 'meta_description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['preview_link']
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'template', 'content')
        }),
        ('Publishing', {
            'fields': ('is_active', 'publish_date')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        })
    )

    def preview_link(self, obj):
        if obj.pk:
            url = reverse('pages:preview', kwargs={'pk': obj.pk})
            return format_html(
                '<a href="{}" target="_blank" class="button">Preview</a>',
                url
            )
        return "Save first to preview"
    preview_link.short_description = "Preview"

    def save_model(self, request, obj, form, change):
        # Ensure only one homepage exists
        if obj.template == 'home':
            Page.objects.filter(template='home').exclude(pk=obj.pk).update(template='about')
        super().save_model(request, obj, form, change)

@admin.register(AboutMe)
class AboutMeAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active']
    fields = ['title', 'subtitle', 'description', 'qualifications', 'image', 'is_active']

    def save_model(self, request, obj, form, change):
        if obj.is_active:
            AboutMe.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)

@admin.register(AboutTuition)
class AboutTuitionAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active']
    fields = ['title', 'description', 'booking_title', 'booking_description', 
              'booking_button_text', 'booking_button_url', 'is_active']

    def save_model(self, request, obj, form, change):
        if obj.is_active:
            AboutTuition.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)

@admin.register(AboutCourses)
class AboutCoursesAdmin(admin.ModelAdmin):
    list_display = ['title', 'show_courses_section', 'is_active']
    fields = ['title', 'description', 'show_courses_section', 'button_text', 'is_active']

    def save_model(self, request, obj, form, change):
        if obj.is_active:
            AboutCourses.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)
