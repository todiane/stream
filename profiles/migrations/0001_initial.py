# Generated by Django 5.1.2 on 2024-11-30 12:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30)),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('enrolled_courses', models.ManyToManyField(blank=True, related_name='enrolled_students', to='courses.course')),
                ('last_watched_lesson', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='last_watched_by', to='courses.lesson')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('watched_videos', models.ManyToManyField(blank=True, related_name='watched_by', to='courses.lesson')),
            ],
        ),
    ]
