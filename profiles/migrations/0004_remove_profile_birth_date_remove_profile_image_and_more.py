# Generated by Django 5.1.2 on 2024-10-16 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_lesson_youtube_url'),
        ('profiles', '0003_profile_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='birth_date',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='image',
        ),
        migrations.AddField(
            model_name='profile',
            name='enrolled_courses',
            field=models.ManyToManyField(blank=True, related_name='enrolled_students', to='courses.course'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='first_name',
            field=models.CharField(max_length=30),
        ),
    ]