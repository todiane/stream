from django.core.management.base import BaseCommand
from shop.models import Product

class Command(BaseCommand):
    help = 'Update purchase counts for all products based on completed orders'

    def handle(self, *args, **kwargs):
        for product in Product.objects.all():
            order_items = product.order_items.filter(order__status='completed')
            total_quantity = sum(item.quantity for item in order_items)
            product.purchase_count = total_quantity
            product.save()
            self.stdout.write(f'Updated {product.title}: {total_quantity} purchases')
            