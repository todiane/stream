# Generated by Django 4.2.10 on 2024-12-18 19:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shop', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30)),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('email_subscribed', models.BooleanField(default=True)),
                ('email_verified', models.BooleanField(default=False)),
                ('enrolled_courses', models.ManyToManyField(blank=True, related_name='enrolled_students', to='courses.course')),
                ('last_watched_lesson', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='last_watched_by', to='courses.lesson')),
                ('purchased_products', models.ManyToManyField(blank=True, related_name='purchasers', to='shop.product')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('watched_videos', models.ManyToManyField(blank=True, related_name='watched_by', to='courses.lesson')),
            ],
        ),
        migrations.CreateModel(
            name='ContactSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(choices=[('general', 'General Inquiry'), ('tuition', 'Tuition Inquiry'), ('technical', 'Technical Support'), ('other', 'Other')], max_length=20)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('parent_first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('parent_last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('parent_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('parent_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
