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

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'email', 'paid', 'created', 'get_customer_name']
    list_filter = ['paid', 'created', 'status']
    search_fields = ['order_id', 'user__username', 'email', 
                    'guest_details__first_name', 'guest_details__last_name']
    inlines = [OrderItemInline]
    readonly_fields = ['order_id', 'payment_intent_id', 'guest_details_display']

    def get_customer_name(self, obj):
        if obj.user:
            return f"{obj.user.profile.first_name}"
        elif hasattr(obj, 'guest_details'):
            return f"{obj.guest_details.first_name} {obj.guest_details.last_name} (Guest)"
        return "No name provided"
    get_customer_name.short_description = "Customer"

    def guest_details_display(self, obj):
        if hasattr(obj, 'guest_details'):
            return format_html(
                '<strong>Name:</strong> {} {}<br>'
                '<strong>Email:</strong> {}<br>'
                '<strong>Phone:</strong> {}',
                obj.guest_details.first_name,
                obj.guest_details.last_name,
                obj.guest_details.email,
                obj.guest_details.phone or 'Not provided'
            )
        return "No guest details"
    guest_details_display.short_description = "Guest Details"

    fieldsets = (
        (None, {
            'fields': ('order_id', 'user', 'email', 'status', 'paid')
        }),
        ('Guest Information', {
            'fields': ('guest_details_display',),
            'classes': ('collapse',)
        }),
        ('Payment Information', {
            'fields': ('payment_intent_id',),
            'classes': ('collapse',)
        }),
    )