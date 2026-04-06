from django.core.management.base import BaseCommand
from apps.orders.tasks import auto_cancel_expired_orders

class Command(BaseCommand):
    help = 'Auto-cancel expired pickup orders'

    def handle(self, *args, **kwargs):
        count = auto_cancel_expired_orders()
        self.stdout.write(f"Cancelled {count} expired orders.")