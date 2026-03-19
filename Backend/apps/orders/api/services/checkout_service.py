# apps/orders/api/services/checkout_service.py
from decimal import Decimal
from django.db import transaction
from apps.orders.models import Order, OrderItem, OrderStatusHistory
from apps.deliveries.models import Delivery


class CheckoutError(Exception):
    pass


def _is_pickup(delivery_data):
    address = delivery_data.get("delivery_address", "")
    return address.startswith("PICKUP —")


@transaction.atomic
def place_order(user, delivery_data):
    cart  = _get_cart_or_raise(user)
    items = list(cart.items.select_related("product__shop", "cut_type").all())

    if not items:
        raise CheckoutError("Your cart is empty.")

    _validate_stock(items)

    created_orders = []
    for shop, shop_items in _group_by_shop(items).items():
        order = _create_order(user, shop, shop_items, delivery_data)
        created_orders.append(order)

    cart.items.all().delete()
    return created_orders


def _get_cart_or_raise(user):
    try:
        return user.cart
    except Exception:
        raise CheckoutError("No cart found.")


def _validate_stock(items):
    for item in items:
        product = item.product
        if not product.is_available:
            raise CheckoutError(f"{product.name} is not available.")
        if item.quantity and product.stock_quantity < item.quantity:
            raise CheckoutError(
                f"Only {product.stock_quantity}{product.unit} of "
                f"{product.name} is in stock."
            )


def _group_by_shop(items):
    buckets = {}
    for item in items:
        buckets.setdefault(item.product.shop, []).append(item)
    return buckets


def _create_order(user, shop, items, delivery_data):
    subtotal  = sum(item.subtotal for item in items)
    is_pickup = _is_pickup(delivery_data)
    fee       = Decimal("0.00") if is_pickup else shop.delivery_charge
    total     = subtotal + fee

    order = Order.objects.create(
        customer         = user,
        shop             = shop,
        subtotal         = subtotal,
        delivery_fee     = fee,
        total_amount     = total,
        payment_method   = delivery_data.get("payment_method", Order.PaymentMethod.COD),
        delivery_name    = delivery_data["delivery_name"],
        delivery_phone   = delivery_data["delivery_phone"],
        delivery_address = delivery_data["delivery_address"],
        notes            = delivery_data.get("notes", ""),
    )

    for item in items:
        OrderItem.objects.create(
            order         = order,
            product       = item.product,
            product_name  = item.product.name,
            cut_type_name = item.cut_type.name if item.cut_type else "",
            quantity      = item.quantity,
            unit_price    = item.price_at_time,
        )
        item.product.stock_quantity -= item.quantity
        item.product.save(update_fields=["stock_quantity"])

    OrderStatusHistory.objects.create(
        order       = order,
        from_status = "",
        to_status   = Order.Status.PENDING,
        changed_by  = user,
        note        = "Order placed",
    )
    Delivery.objects.create(order=order)
    return order