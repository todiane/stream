# Generated by Django 5.1.2 on 2024-12-09 22:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_rename_submitted_at_contactsubmission_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='email_verified',
            field=models.BooleanField(default=False),
        ),
    ]
