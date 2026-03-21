# apps/orders/models.py
from django.db import models


class Order(models.Model):

    class Status(models.TextChoices):
        PENDING          = "pending",          "Pending"
        CONFIRMED        = "confirmed",        "Confirmed"
        PREPARING        = "preparing",        "Preparing"
        OUT_FOR_DELIVERY = "out_for_delivery", "Out for Delivery"
        DELIVERED        = "delivered",        "Delivered"
        CANCELLED        = "cancelled",        "Cancelled"

    class PaymentMethod(models.TextChoices):
        COD    = "cod",    "Cash on Delivery"
        ONLINE = "online", "Online Payment"

    VALID_TRANSITIONS = {
        Status.PENDING:          [Status.CONFIRMED, Status.CANCELLED],
        Status.CONFIRMED:        [Status.PREPARING, Status.CANCELLED],
        Status.PREPARING:        [Status.OUT_FOR_DELIVERY],
        Status.OUT_FOR_DELIVERY: [Status.DELIVERED],
        Status.DELIVERED:        [],
        Status.CANCELLED:        [],
    }

    customer         = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="orders",
    )
    shop             = models.ForeignKey(
        "shops.Shop",
        on_delete=models.CASCADE,
        related_name="orders",
    )
    status           = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
    )
    payment_method   = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.COD,
    )
    subtotal         = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_name    = models.CharField(max_length=255)
    delivery_phone   = models.CharField(max_length=20)
    delivery_address = models.TextField()
    notes            = models.TextField(blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    def can_transition_to(self, new_status):
        return new_status in self.VALID_TRANSITIONS.get(self.status, [])

    def __str__(self):
        return f"Order #{self.pk} — {self.customer} → {self.shop}"


class OrderItem(models.Model):
    order         = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product       = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
    )
    # Snapshots — product may be renamed or deleted later
    product_name  = models.CharField(max_length=255)
    cut_type_name = models.CharField(max_length=100, blank=True)
    quantity      = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price    = models.DecimalField(max_digits=10, decimal_places=2)
    total_price   = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class OrderStatusHistory(models.Model):
    """Every status change is recorded here — full audit trail."""
    order       = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="history",
    )
    from_status = models.CharField(max_length=30, blank=True)
    to_status   = models.CharField(max_length=30)
    changed_by  = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
    )
    note        = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Order #{self.order.pk}: {self.from_status} → {self.to_status}"