from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings
from stream.storage import secure_storage, public_storage
import uuid
from ckeditor_uploader.fields import RichTextUploadingField


def generate_public_id(instance, *args, **kwargs):
    title = instance.title
    unique_id = str(uuid.uuid4()).replace("-", "")
    if not title:
        return unique_id
    slug = slugify(title)
    unique_id_short = unique_id[:5]
    return f"{slug}-{unique_id_short}"


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shop:category", kwargs={"slug": self.slug})


class Product(models.Model):
    STATUS_CHOICES = [
        ("publish", "Published"),
        ("soon", "Coming Soon"),
        ("draft", "Draft"),
    ]
    PRODUCT_TYPES = [("download", "Digital Download"), ("tuition", "Tuition Hours")]

    # Basic Fields
    public_id = models.CharField(max_length=130, blank=True, null=True, db_index=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    description = RichTextUploadingField()
    product_type = models.CharField(
        max_length=20, choices=PRODUCT_TYPES, default="download"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    is_active = models.BooleanField(default=True)

    # Pricing
    price_pence = models.PositiveIntegerField(help_text="Price in pence")
    sale_price_pence = models.PositiveIntegerField(
        null=True, blank=True, help_text="Sale price in pence"
    )
    price_per_hour = models.PositiveIntegerField(
        null=True, blank=True, help_text="Tuition price per hour in pence"
    )

    # Media
    files = models.FileField(
        upload_to="products/files/", null=True, blank=True, storage=secure_storage
    )
    preview_file = models.FileField(
        upload_to="products/previews/", null=True, blank=True, storage=public_storage
    )
    preview_image = models.ImageField(
        upload_to="products/images/", null=True, blank=True, storage=public_storage
    )

    # Settings
    download_limit = models.PositiveIntegerField(default=5)
    featured = models.BooleanField(default=False)
    purchase_count = models.PositiveIntegerField(default=0)

    # Timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.public_id:
            self.public_id = generate_public_id(self)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("shop:product_detail", kwargs={"slug": self.slug})

    def get_download_url(self):
        if self.files:
            return self.files.url
        return None

    @property
    def price(self):
        """Return price in pounds"""
        return self.price_pence / 100

    @property
    def sale_price(self):
        """Return sale price in pounds if it exists"""
        if self.sale_price_pence:
            return self.sale_price_pence / 100
        return None

    @property
    def current_price(self):
        """Return the current applicable price in pounds"""
        if self.sale_price_pence:
            return self.sale_price
        return self.price

    @property
    def is_on_sale(self):
        return bool(self.sale_price_pence)


class GuestDetails(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.OneToOneField(
        "Order", on_delete=models.CASCADE, related_name="guest_details"
    )

    class Meta:
        verbose_name_plural = "Guest Details"

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    order_id = models.CharField(max_length=100, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    email = models.EmailField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_intent_id = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"Order {self.order_id}"

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f"ORD-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    @property
    def total_price(self):
        return self.get_total_cost()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="order_items", on_delete=models.CASCADE
    )
    price_paid_pence = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)
    downloads_remaining = models.PositiveIntegerField(default=5)
    download_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price_paid_pence * self.quantity
