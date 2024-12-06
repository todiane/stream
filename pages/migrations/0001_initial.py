# Generated by Django 5.1.2 on 2024-12-06 07:45

import django.db.models.deletion
import django.utils.timezone
import django_ckeditor_5.fields
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Hero',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('subtitle', models.CharField(blank=True, max_length=200)),
                ('content', django_ckeditor_5.fields.CKEditor5Field(blank=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Hero Section',
                'verbose_name_plural': 'Hero Section',
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta_title', models.CharField(blank=True, help_text='SEO Title (60 characters max)', max_length=60)),
                ('meta_description', models.CharField(blank=True, help_text='SEO Description (160 characters max)', max_length=160)),
                ('meta_keywords', models.CharField(blank=True, help_text='Comma-separated keywords', max_length=255)),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('content', django_ckeditor_5.fields.CKEditor5Field()),
                ('template', models.CharField(choices=[('home', 'Homepage'), ('about', 'About Page')], max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('publish_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='HistoricalPage',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('meta_title', models.CharField(blank=True, help_text='SEO Title (60 characters max)', max_length=60)),
                ('meta_description', models.CharField(blank=True, help_text='SEO Description (160 characters max)', max_length=160)),
                ('meta_keywords', models.CharField(blank=True, help_text='Comma-separated keywords', max_length=255)),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField()),
                ('content', django_ckeditor_5.fields.CKEditor5Field()),
                ('template', models.CharField(choices=[('home', 'Homepage'), ('about', 'About Page')], max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('publish_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical page',
                'verbose_name_plural': 'historical pages',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
