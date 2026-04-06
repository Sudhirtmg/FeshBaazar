# apps/b2b/management/commands/backfill_ledger.py
from django.core.management.base import BaseCommand
from django.db.models import Sum
from apps.b2b.models import B2BOrder, LedgerEntry


class Command(BaseCommand):
    help = "Backfill missing ledger credit entries for existing orders"

    def handle(self, *args, **kwargs):
        orders_with_entries = LedgerEntry.objects.filter(
            entry_type="credit"
        ).values_list("order_id", flat=True)

        missing = B2BOrder.objects.exclude(
            id__in=orders_with_entries
        ).filter(
            total_price__isnull=False,
            total_price__gt=0,
        ).order_by("id")

        self.stdout.write(f"Found {missing.count()} orders missing ledger entries")

        created = 0
        for order in missing:
            total_credit = LedgerEntry.objects.filter(
                shop=order.shop, entry_type="credit"
            ).aggregate(total=Sum("amount"))["total"] or 0

            total_payment = LedgerEntry.objects.filter(
                shop=order.shop, entry_type="payment"
            ).aggregate(total=Sum("amount"))["total"] or 0

            new_balance = (total_credit - total_payment) + (order.total_price or 0)

            LedgerEntry.objects.create(
                shop=order.shop,
                cold_storage=order.cold_storage,
                order=order,
                amount=order.total_price,
                entry_type="credit",
                balance_after=new_balance,
                note=f"Backfill: {order.payment_type} order #{order.id}",
            )
            created += 1
            self.stdout.write(f"  ✓ Order #{order.id} — {order.shop.name} — ₹{order.total_price}")

        self.stdout.write(self.style.SUCCESS(f"\nDone. Created {created} ledger entries."))