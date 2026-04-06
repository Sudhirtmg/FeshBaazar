#  Create auto-cancel task 
# Backend/apps/orders/tasks.py:

from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

def auto_cancel_expired_orders():
    """
    Cancel pickup orders where customer didn't arrive within 15 mins
    of scheduled time. Run this every 5 minutes via a cron job.
    """
    from apps.orders.models import Order
    from apps.orders.api.services.status_service import advance_order_status

    now = timezone.now()
    grace_period = timedelta(minutes=15)

    expired_orders = Order.objects.filter(
        fulfillment_type=Order.FulfillmentType.PICKUP,
        scheduled_time__isnull=False,
        scheduled_time__lt=now - grace_period,
        status__in=[Order.Status.PENDING, Order.Status.CONFIRMED],
    )

    cancelled_count = 0
    for order in expired_orders:
        try:
            advance_order_status(
                order,
                Order.Status.CANCELLED,
                changed_by=None,
                note="Auto-cancelled: customer did not arrive within 15 minutes of scheduled time.",
            )
            cancelled_count += 1
            logger.info(f"Auto-cancelled Order #{order.pk}")
        except Exception as e:
            logger.error(f"Failed to auto-cancel Order #{order.pk}: {e}")

    return cancelled_count