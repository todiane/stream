import helpers
from django.contrib import admin
from django.utils.html import format_html
from .models import Course, Lesson, Category
import django_ckeditor_5.widgets

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam_board', 'slug']
    list_filter = ['exam_board']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

class LessonInline(admin.StackedInline):
    model = Lesson
    readonly_fields = [
        'public_id', 
        'updated', 
        'display_image',
        'display_video',
    ]
    extra = 0

    def display_image(self, obj, *args, **kwargs):
        url = helpers.get_cloudinary_image_object(
            obj, 
            field_name='thumbnail',
            width=200
        )
        return format_html(f"<img src={url} />")

    display_image.short_description = "Current Image"

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'description':
            kwargs['widget'] = django_ckeditor_5.widgets.CKEditor5Widget(
                config_name='default',
                attrs={'class': 'django_ckeditor_5'}
            )
        return super().formfield_for_dbfield(db_field, **kwargs)

    def display_video(self, obj, *args, **kwargs):
        video_embed_html = helpers.get_cloudinary_video_object(
            obj, 
            field_name='video',
            as_html=True,
            width=550
        )
        return video_embed_html

    display_video.short_description = "Current Video"

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):  
    inlines = [LessonInline]
    list_display = ['title', 'category', 'status', 'access', 'public_id']
    list_filter = ['status', 'access', 'category', 'category__exam_board']
    fields = ['public_id', 'title', 'slug', 'description', 'category', 'status', 'image', 'access', 'display_image']
    readonly_fields = ['public_id', 'display_image']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'description', 'category__name', 'slug']

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'description':
            kwargs['widget'] = django_ckeditor_5.widgets.CKEditor5Widget(
                config_name='default',
                attrs={'class': 'django_ckeditor_5'}
            )
        return super().formfield_for_dbfield(db_field, **kwargs)

    def display_image(self, obj, *args, **kwargs):
        url = helpers.get_cloudinary_image_object(
            obj, 
            field_name='image',
            width=200
        )
        return format_html(f"<img src={url} />")

    display_image.short_description = "Current Image"
    