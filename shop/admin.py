from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
import requests
from .models import Category, Product, Order, OrderItem, ProductReview


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "description"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "category",
        "status",
        "price",
        "sale_price",
        "product_type",
        "purchase_count",
        "featured",
        "display_thumbnail",
        "order",
    ]
    list_filter = ["status", "category", "product_type", "featured", "created"]
    search_fields = ["title", "description", "public_id"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = [
        "public_id",
        "purchase_count",
        "display_preview",
        "download_file",
    ]
    list_editable = ["order"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "public_id",
                    "title",
                    "slug",
                    "category",
                    "description",
                    "product_type",
                    "number_of_pages",
                    "status",
                    "is_active",
                )
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "price_pence",
                    "sale_price_pence",
                    "price_per_hour",
                )
            },
        ),
        (
            "Media",
            {
                "fields": (
                    "preview_image",
                    "external_image_url",
                    "files",
                    "download_file",
                    "preview_file",
                    "external_preview_url",
                ),
            },
        ),
        (
            "Settings",
            {
                "fields": (
                    "download_limit",
                    "featured",
                    "purchase_count",
                    "order",
                )
            },
        ),
    )

    def price(self, obj):
        return f"£{obj.price:.2f}"

    def sale_price(self, obj):
        if obj.sale_price_pence:
            return f"£{obj.sale_price:.2f}"
        return "-"

    def display_thumbnail(self, obj):
        image_url = obj.get_image_url()
        if image_url:
            return format_html(
                '<img src="{}" width="50" class="admin-thumbnail" style="border-radius: 3px;" />',
                image_url,
            )
        return "-"

    display_thumbnail.short_description = "Thumbnail"

    def display_preview(self, obj):
        html = []
        image_url = obj.get_image_url()
        if image_url:
            html.append(
                f'<div class="mb-4"><strong>Preview Image:</strong><br/>'
                f'<img src="{image_url}" width="200" style="border-radius: 5px; '
                f'box-shadow: 0 2px 5px rgba(0,0,0,0.1);" /></div>'
            )
        return format_html("".join(html)) if html else "-"

    display_preview.short_description = "Preview"

    def download_file(self, obj):
        if obj.pk and obj.files and obj.files.name:
            url = reverse("shop:staff_download", args=[obj.pk])
            return format_html(
                '<a href="{}" class="button" target="_blank">Download file</a>', url
            )
        return "Save the product with a file uploaded to enable download."

    download_file.short_description = "Download uploaded file"

    def clean_external_preview_url(self, url):
        if not url:
            return url

        # Validate URL format
        validator = URLValidator()
        try:
            validator(url)
        except ValidationError:
            raise ValidationError("Invalid URL format")

        # Check if URL exists and is a PDF
        try:
            response = requests.head(url, allow_redirects=True)
            content_type = response.headers.get("content-type", "").lower()

            if not content_type == "application/pdf":
                raise ValidationError("URL must point to a PDF file")

        except requests.RequestException:
            raise ValidationError("Could not validate preview URL")

        return url

    def save_model(self, request, obj, form, change):
        if "external_image_url" in form.changed_data:
            obj.external_image_url = self.clean_external_image_url(
                obj.external_image_url
            )
        if "external_preview_url" in form.changed_data:
            obj.external_preview_url = self.clean_external_preview_url(
                obj.external_preview_url
            )
        super().save_model(request, obj, form, change)

    def clean_external_image_url(self, url):
        if not url:
            return url

        # Validate URL format
        validator = URLValidator()
        try:
            validator(url)
        except ValidationError:
            raise ValidationError("Invalid URL format")

        # Check if URL exists and is an image
        try:
            response = requests.head(url, allow_redirects=True)
            content_type = response.headers.get("content-type", "").lower()

            if not content_type.startswith("image/"):
                raise ValidationError("URL must point to an image file")

            if not any(content_type.endswith(ext) for ext in ["/jpeg", "/jpg", "/png"]):
                raise ValidationError("Only JPG and PNG images are allowed")

        except requests.RequestException:
            raise ValidationError("Could not validate image URL")

        return url


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ["product"]
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # NOTE: this previously referenced a GuestDetails model/relation
    # (guest checkout support) that no longer exists in models.py - guest
    # checkout was removed and checkout() now requires login. The old
    # search_fields entries ("guest_details__first_name" etc.) referenced a
    # field that doesn't exist, so searching orders in the admin raised a
    # FieldError. Cleaned up to match the current login-required checkout.
    list_display = ["order_id", "user", "email", "paid", "created", "get_customer_name"]
    list_filter = ["paid", "created", "status"]
    search_fields = [
        "order_id",
        "user__username",
        "email",
    ]
    inlines = [OrderItemInline]
    readonly_fields = ["order_id", "payment_intent_id"]

    def get_customer_name(self, obj):
        if obj.user:
            return obj.user.profile.first_name
        return "No name provided"

    get_customer_name.short_description = "Customer"

    fieldsets = (
        (None, {"fields": ("order_id", "user", "email", "status", "paid")}),
        (
            "Payment Information",
            {"fields": ("payment_intent_id",), "classes": ("collapse",)},
        ),
    )


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ["product", "user", "rating", "verified_purchase", "created"]
    list_filter = ["rating", "verified_purchase", "created"]
    search_fields = ["product__title", "user__username", "comment"]
    readonly_fields = ["verified_purchase"]
