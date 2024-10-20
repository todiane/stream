# Generated by Django 5.1.2 on 2024-10-19 15:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_lesson_youtube_url'),
        ('profiles', '0004_remove_profile_birth_date_remove_profile_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='last_watched_lesson',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='last_watched_by', to='courses.lesson'),
        ),
        migrations.AddField(
            model_name='profile',
            name='watched_videos',
            field=models.ManyToManyField(blank=True, related_name='watched_by', to='courses.lesson'),
        ),
    ]
