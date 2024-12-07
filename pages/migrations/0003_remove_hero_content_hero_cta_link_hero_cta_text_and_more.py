# Generated by Django 5.1.2 on 2024-12-06 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_initial_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hero',
            name='content',
        ),
        migrations.AddField(
            model_name='hero',
            name='cta_link',
            field=models.CharField(blank=True, max_length=200, verbose_name='Call to Action Link'),
        ),
        migrations.AddField(
            model_name='hero',
            name='cta_text',
            field=models.CharField(blank=True, default='Learn more', max_length=50, verbose_name='Call to Action Text'),
        ),
        migrations.AddField(
            model_name='hero',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='hero',
            name='video_url',
            field=models.URLField(blank=True, help_text='YouTube video URL (e.g., https://www.youtube.com/watch?v=xxxxx)'),
        ),
    ]