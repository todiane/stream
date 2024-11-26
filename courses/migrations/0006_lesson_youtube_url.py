# Generated by Django 5.1.2 on 2024-10-13 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_alter_course_image_lesson'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='youtube_url',
            field=models.URLField(blank=True, help_text='Enter a YouTube URL if you want to embed a video from YouTube.', null=True),
        ),
    ]
