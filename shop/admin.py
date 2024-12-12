from django.contrib import admin
from django.utils.html import format_html
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Category, Product, Order, OrderItem
import helpers

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'price', 'sale_price', 
                   'product_type', 'purchase_count', 'featured']
    list_filter = ['status', 'category', 'product_type', 'featured', 'created']
    search_fields = ['title', 'description', 'public_id']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['public_id', 'purchase_count', 'display_preview']

    fieldsets = (
        (None, {
            'fields': ('public_id', 'title', 'slug', 'category', 'description',
                      'product_type', 'status', 'featured')
        }),
        ('Pricing', {
            'fields': ('price_pence', 'sale_price_pence', 'price_per_hour'),
        }),
        ('Files', {
            'fields': ('files', 'preview_file', 'preview_image', 'display_preview'),
        }),
        ('Settings', {
            'fields': ('download_limit', 'purchase_count'),
        }),
    )

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'description':
            kwargs['widget'] = CKEditor5Widget(
                config_name='default',
                attrs={'class': 'django_ckeditor_5'}
            )
        return super().formfield_for_dbfield(db_field, **kwargs)

    def display_preview(self, obj):
        html = []
        if obj.preview_image:
            url = helpers.get_cloudinary_image_object(obj, 'preview_image', width=200)
            html.append(f'<div class="mb-4"><strong>Preview Image:</strong><br/>'
                       f'<img src="{url}" /></div>')
        return format_html(''.join(html)) if html else '-'
    
    display_preview.short_description = "Preview"

    def price(self, obj):
        return f"£{obj.price:.2f}"
    
    def sale_price(self, obj):
        if obj.sale_price_pence:
            return f"£{obj.sale_price:.2f}"
        return "-"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'email', 'paid', 'created']
    list_filter = ['paid', 'created']
    search_fields = ['order_id', 'user__username', 'email']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    readonly_fields = ['price_paid_pence', 'downloads_remaining']
    extra = 0