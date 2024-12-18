# Generated by Django 4.2.10 on 2024-12-18 19:59

import ckeditor_uploader.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import stream.storage


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(editable=False, max_length=100, unique=True)),
                ('email', models.EmailField(max_length=254)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('paid', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('payment_intent_id', models.CharField(blank=True, max_length=250)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_id', models.CharField(blank=True, db_index=True, max_length=130, null=True)),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('description', ckeditor_uploader.fields.RichTextUploadingField()),
                ('product_type', models.CharField(choices=[('download', 'Digital Download'), ('tuition', 'Tuition Hours')], default='download', max_length=20)),
                ('status', models.CharField(choices=[('publish', 'Published'), ('soon', 'Coming Soon'), ('draft', 'Draft')], default='draft', max_length=10)),
                ('is_active', models.BooleanField(default=True)),
                ('price_pence', models.PositiveIntegerField(help_text='Price in pence')),
                ('sale_price_pence', models.PositiveIntegerField(blank=True, help_text='Sale price in pence', null=True)),
                ('price_per_hour', models.PositiveIntegerField(blank=True, help_text='Tuition price per hour in pence', null=True)),
                ('files', models.FileField(blank=True, null=True, storage=stream.storage.SecureFileStorage(), upload_to='products/files/')),
                ('preview_file', models.FileField(blank=True, null=True, storage=stream.storage.PublicMediaStorage(), upload_to='products/previews/')),
                ('preview_image', models.ImageField(blank=True, null=True, storage=stream.storage.PublicMediaStorage(), upload_to='products/images/')),
                ('download_limit', models.PositiveIntegerField(default=5)),
                ('featured', models.BooleanField(default=False)),
                ('purchase_count', models.PositiveIntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shop.category')),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_paid_pence', models.PositiveIntegerField()),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('downloads_remaining', models.PositiveIntegerField(default=5)),
                ('download_count', models.PositiveIntegerField(default=0)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='shop.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='shop.product')),
            ],
        ),
        migrations.CreateModel(
            name='GuestDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='guest_details', to='shop.order')),
            ],
            options={
                'verbose_name_plural': 'Guest Details',
            },
        ),
    ]
