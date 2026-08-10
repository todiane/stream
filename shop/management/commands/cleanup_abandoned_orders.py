from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from shop.models import Order


class Command(BaseCommand):
    help = (
        "Mark stale 'pending' orders as 'cancelled'. These are orders created at "
        "the start of checkout that were never completed (the user abandoned "
        "payment, closed the tab, etc). Run this periodically, e.g. daily via cron."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--hours",
            type=int,
            default=24,
            help="Cancel pending orders older than this many hours (default: 24).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be cancelled without making changes.",
        )

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(hours=options["hours"])
        stale_orders = Order.objects.filter(status="pending", created__lt=cutoff)

        count = stale_orders.count()
        if count == 0:
            self.stdout.write("No abandoned pending orders found.")
            return

        if options["dry_run"]:
            for order in stale_orders:
                self.stdout.write(
                    f"Would cancel {order.order_id} (created {order.created})"
                )
            self.stdout.write(f"{count} order(s) would be cancelled (dry run).")
            return

        updated = stale_orders.update(status="cancelled")
        self.stdout.write(
            self.style.SUCCESS(f"Cancelled {updated} abandoned pending order(s).")
        )
