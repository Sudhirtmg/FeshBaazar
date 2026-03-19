# apps/orders/services/status_service.py
from apps.orders.models import Order, OrderStatusHistory


class StatusTransitionError(Exception):
    pass


def advance_order_status(order, new_status, changed_by, note=""):
    if not order.can_transition_to(new_status):
        raise StatusTransitionError(
            f"Cannot move from '{order.status}' to '{new_status}'."
        )
    old_status   = order.status
    order.status = new_status
    order.save(update_fields=["status"])

    OrderStatusHistory.objects.create(
        order       = order,
        from_status = old_status,
        to_status   = new_status,
        changed_by  = changed_by,
        note        = note,
    )
    return order