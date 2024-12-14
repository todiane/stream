from django.core.management.base import BaseCommand
from shop.models import Order
from shop.emails import send_download_link_email

class Command(BaseCommand):
    help = 'Sends a test download link email for the last order'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address to send to')

    def handle(self, *args, **kwargs):
        try:
            # Get the last order
            last_order = Order.objects.filter(status='completed').last()
            if not last_order:
                self.stdout.write(self.style.ERROR('No completed orders found'))
                return

            # Get the first order item
            order_item = last_order.items.first()
            if not order_item:
                self.stdout.write(self.style.ERROR('No items in the last order'))
                return

            # Temporarily change the email
            original_email = last_order.user.email
            last_order.user.email = kwargs['email']
            
            # Send the email
            send_download_link_email(order_item)
            
            # Restore original email
            last_order.user.email = original_email
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully sent test email to {kwargs["email"]}')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to send email: {str(e)}')
            )
