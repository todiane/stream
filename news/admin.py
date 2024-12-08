# news/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Category, Post
import helpers


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'publish_date', 'display_thumbnail']
    list_filter = ['status', 'category', 'created', 'publish_date']
    search_fields = ['title', 'content', 'meta_title', 'meta_description']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'publish_date'

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'content', 'status', 'publish_date'),
        }),
        ('Media', {
            'fields': ('image', 'video', 'youtube_url', 'display_media'),
            'classes': ('collapse',),
        }),
        ('Advertisement', {
            'fields': ('ad_type', 'ad_code', 'ad_image', 'ad_url'),
            'classes': ('collapse',),
        }),
        ('Resource', {
            'fields': ('resource_type', 'resource_title', 'resource'),
            'classes': ('collapse',),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ['display_media']

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'content':
            kwargs['widget'] = CKEditor5Widget(
                config_name='default',
                attrs={'class': 'django_ckeditor_5'}
            )
        return super().formfield_for_dbfield(db_field, **kwargs)

    def display_media(self, obj):
        html = []
        if obj.image:
            url = helpers.get_cloudinary_image_object(obj, 'image', width=200)
            html.append(f'<div class="mb-4"><strong>Image:</strong><br/><img src="{url}" /></div>')
        
        if obj.video:
            video_html = helpers.get_cloudinary_video_object(obj, 'video', as_html=True, width=200)
            html.append(f'<div class="mb-4"><strong>Video:</strong><br/>{video_html}</div>')
        
        if obj.youtube_url:
            html.append(f'<div class="mb-4"><strong>YouTube URL:</strong><br/>{obj.youtube_url}</div>')
        
        # Add resource information
        if obj.resource and obj.resource_type != 'none':
            html.append(f'<div class="mb-4"><strong>Resource:</strong><br/>'
                        f'Type: {obj.get_resource_type_display()}<br/>'
                        f'Title: {obj.resource_title}<br/>'
                        f'<a href="{obj.get_resource_url()}" target="_blank">Download Resource</a></div>')
        
        return format_html(''.join(html)) if html else '-'

    display_media.short_description = "Media Preview"

    def display_thumbnail(self, obj):
        if obj.image:
            url = helpers.get_cloudinary_image_object(obj, 'image', width=50)
            return format_html(f'<img src="{url}" width="50" />')
        return '-'

    display_thumbnail.short_description = "Thumbnail"
