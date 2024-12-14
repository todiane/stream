# Generated by Django 5.1.2 on 2024-12-01 09:47

import cloudinary.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(blank=True)),
                ('exam_board', models.CharField(choices=[('AQA', 'AQA'), ('EDEXCEL', 'Edexcel')], max_length=20)),
            ],
            options={
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('public_id', models.CharField(blank=True, db_index=True, max_length=130, null=True)),
                ('access', models.CharField(choices=[('any', 'Anyone'), ('email', 'Email required')], default='email', max_length=5)),
                ('status', models.CharField(choices=[('publish', 'Published'), ('soon', 'Coming Soon'), ('draft', 'Draft')], default='draft', max_length=10)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('image', cloudinary.models.CloudinaryField(max_length=255, null=True, verbose_name='image')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='courses.category')),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_id', models.CharField(blank=True, db_index=True, max_length=130, null=True)),
                ('title', models.CharField(max_length=120)),
                ('description', models.TextField(blank=True, null=True)),
                ('thumbnail', cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image')),
                ('video', cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='video')),
                ('youtube_url', models.URLField(blank=True, help_text='Enter a YouTube URL if you want to embed a video from YouTube.', null=True)),
                ('order', models.IntegerField(default=0)),
                ('can_preview', models.BooleanField(default=False, help_text='If user does not have access to course, can they see this?')),
                ('status', models.CharField(choices=[('publish', 'Published'), ('soon', 'Coming Soon'), ('draft', 'Draft')], default='publish', max_length=10)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
            ],
            options={
                'ordering': ['order', '-updated'],
            },
        ),
    ]
