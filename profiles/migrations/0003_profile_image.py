# Generated by Django 5.1.2 on 2024-10-14 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_rename_location_profile_first_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='image',
            field=models.ImageField(blank=True, default='profile_images/default.jpg', upload_to='profile_images/'),
        ),
    ]