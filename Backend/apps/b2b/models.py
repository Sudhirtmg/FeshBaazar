# apps/b2b/models.py
from django.db import models
from apps.shops.models import Shop


class ColdStorage(models.Model):
    owner    = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="cold_storage",
    )
    name     = models.CharField(max_length=255)
    latitude  = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    address  = models.TextField(blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Cold Storages"


class ColdStorageProduct(models.Model):

    class Category(models.TextChoices):
        CHICKEN = "chicken", "Chicken"
        BEEF    = "beef",    "Beef"
        BUFFALO = "buffalo", "Buffalo"
        MUTTON  = "mutton",  "Mutton"
        PORK    = "pork",    "Pork"
        SEAFOOD = "seafood", "Seafood"
        OTHER   = "other",   "Other"
    
    #--------------Add-Start----------------
    class UnitType(models.TextChoices):
        KG    = "kg",    "Kilogram"
        PIECE = "piece", "Piece"
    #--------------Add-End----------------
    allowed_units = models.JSONField(
    default=list,
    help_text="['kg'], ['piece'], or ['kg','piece']"
    )


    cold_storage  = models.ForeignKey(
        ColdStorage,
        on_delete=models.CASCADE,
        related_name="products",
    )
    name          = models.CharField(max_length=255)
    category      = models.CharField(
        max_length=50,
        choices=Category.choices,
    )
    price_per_kg = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    null=True,
    blank=True
    )

    stock_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    low_stock_threshold = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=50
    )

    min_order_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=10,
        null=True,
        blank=True
    )
    
    #--------------Add-Start----------------
    # Unit type determines how shop orders this product
    unit_type     = models.CharField(
        max_length=10,
        choices=UnitType.choices,
        default=UnitType.KG,
        help_text="KG = price known upfront. Piece = price set after weighing."
    )
    # For piece-based: approximate weight per piece (informational only, NOT used in price calc)
    approx_weight_per_piece_kg = models.DecimalField(
        max_digits=6, decimal_places=3,
        null=True, blank=True,
        help_text="Approximate kg per piece. Shown to buyer as reference only. Supplier must weigh manually."
    )
    stock_pieces  = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Available stock in pieces (used when unit_type=piece)"
    )
    #--------------Add-End----------------
    
    is_available  = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.cold_storage.name})"


class B2BOrder(models.Model):

    class Meta:
        ordering = ['-created_at']
    class Status(models.TextChoices):
        PENDING_PRICE = "pending_price", "Pending Price"  # piece orders waiting to be weighed
        PRICED        = "priced",        "Priced"          # supplier entered weight + price
        PENDING    = "pending",    "Pending"
        CONFIRMED  = "confirmed",  "Confirmed"
        PROCESSING = "processing", "Processing"
        DISPATCHED = "dispatched", "Dispatched"
        DELIVERED  = "delivered",  "Delivered"
        CANCELLED  = "cancelled",  "Cancelled"
        
    class DeliveryType(models.TextChoices):
        PICKUP   = "pickup",   "Pickup"
        DELIVERY = "delivery", "Delivery"
    
    class PaymentType(models.TextChoices):
        CASH = "cash", "Cash"
        CREDIT = "credit", "Credit"

    payment_type = models.CharField(
        max_length=10,
        choices=PaymentType.choices,
        default=PaymentType.CASH
    )
    class OrderSource(models.TextChoices):
        APP = "app", "App"
        PHONE = "phone", "Phone"
        WALKIN = "walkin", "Walk-in"

    order_source = models.CharField(
        max_length=10,
        choices=OrderSource.choices,
        default="app"
    )
    created_by = models.ForeignKey(
    "accounts.User",
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
    related_name="created_orders"
)

    # mirrors your Order.VALID_TRANSITIONS pattern
    VALID_TRANSITIONS = {
        Status.PENDING_PRICE: [Status.PRICED,     Status.CANCELLED],
        Status.PRICED:        [Status.CONFIRMED,   Status.CANCELLED],
        Status.PENDING:       [Status.CONFIRMED,   Status.CANCELLED],
        Status.CONFIRMED:     [Status.PROCESSING, Status.CANCELLED],
        Status.PROCESSING: [Status.DISPATCHED],
        Status.DISPATCHED: [Status.DELIVERED],
        Status.DELIVERED:  [],
        Status.CANCELLED:  [],
    }

    shop         = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="b2b_orders",
    )
    cold_storage = models.ForeignKey(
        ColdStorage,
        on_delete=models.CASCADE,
        related_name="incoming_orders",
    )
    status       = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    total_price  = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    delivery_latitude  = models.FloatField(null=True, blank=True)
    delivery_longitude = models.FloatField(null=True, blank=True)
    notes        = models.TextField(blank=True)
    delivery_type    = models.CharField(
        max_length=10,
        choices=DeliveryType.choices,
        default=DeliveryType.PICKUP,
    )
    delivery_address = models.TextField(blank=True)
    
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    paid_amount = models.DecimalField(
    max_digits=12,
    decimal_places=2,
    default=0
    )   
    
    # Future-ready: add delivery_fee here when you implement fee logic
    # delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    def remaining_amount(self):
        return max((self.total_price or 0) - self.paid_amount, 0)
    
    #--------------Add-Start----------------
    @property
    def is_paid(self):
        return (self.total_price or 0) <= self.paid_amount

    @property
    def payment_status(self):
        total = self.total_price or 0
        paid = self.paid_amount or 0

        if total <= 0:
            return "unpaid"

        if paid >= total:
            return "paid"
        elif paid > 0:
            return "partial"
        else:
            return "unpaid"
    #--------------Add-End----------------

    def can_transition_to(self, new_status):
        # mirrors Order.can_transition_to()
        return new_status in self.VALID_TRANSITIONS.get(self.status, [])

    def recalculate_total(self):
        total = sum(
            item.line_total for item in self.items.all()
            if item.line_total is not None
        )
        has_unpriced = self.items.filter(line_total__isnull=True).exists()
        self.total_price = None if has_unpriced else total
        self.save(update_fields=["total_price"])

    def __str__(self):
        return f"B2BOrder #{self.pk} — {self.shop.name} → {self.cold_storage.name}"


class B2BOrderItem(models.Model):
    #--------------Add-Start----------------
    class UnitType(models.TextChoices):
        KG    = "kg",    "Kilogram"
        PIECE = "piece", "Piece"
    #--------------Add-End----------------
    order                  = models.ForeignKey(
        B2BOrder,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product                = models.ForeignKey(
        ColdStorageProduct,
        on_delete=models.PROTECT,   # same as your OrderItem uses SET_NULL — PROTECT is safer for B2B
        related_name="order_items",
    )
    # Snapshots — mirrors product_name/unit_price pattern in your OrderItem
    product_name_snapshot  = models.CharField(max_length=255)
    unit_type = models.CharField(
        max_length=10,
        choices=[("kg", "Kilogram"), ("piece", "Piece")],   
        default="kg",
    )
    quantity_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    price_per_kg_snapshot  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    

   
    # For kg orders: quantity is in kg. For piece orders: quantity is number of pieces
    quantity    = models.DecimalField(max_digits=10, decimal_places=2)

    # For piece orders: NULL until supplier weighs + prices
    # For kg orders: calculated immediately = quantity * price_per_kg
    actual_weight_kg  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Filled by supplier after weighing (piece orders only)")
    price_per_kg_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Final price per kg set by supplier (piece orders)")
    line_total  = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="NULL for piece orders until supplier prices them")
    #--------------Add-End----------------
    price                  = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if self.unit_type == "kg" and self.price_per_kg_snapshot:
            if self.price_per_kg_snapshot and self.quantity:
                self.quantity_kg = self.quantity
                self.line_total = self.quantity * self.price_per_kg_snapshot
                self.price = self.line_total  # keep price field for backwards compat
        # piece orders: line_total stays NULL until set_price is called
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name_snapshot} ({self.unit_type})"


class B2BOrderStatusHistory(models.Model):
    """Mirrors OrderStatusHistory — full audit trail for B2B orders."""
    order       = models.ForeignKey(
        B2BOrder,
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
        return f"B2BOrder #{self.order.pk}: {self.from_status} → {self.to_status}"
    
    
class LedgerEntry(models.Model):
    class EntryType(models.TextChoices):
        CREDIT = "credit", "Credit (Udhar Given)"
        PAYMENT = "payment", "Payment Received"
        
    collected_by = models.ForeignKey(
    "accounts.User",
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
    related_name="collected_entries"
    )   
    weighted_by = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL, related_name="weighted_entries")

    shop = models.ForeignKey("shops.Shop", on_delete=models.CASCADE)
    cold_storage = models.ForeignKey("b2b.ColdStorage", on_delete=models.CASCADE)

    order = models.ForeignKey("b2b.B2BOrder", on_delete=models.CASCADE, null=True, blank=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(
    max_digits=12,
    decimal_places=2,
    default=0
    )
    entry_type = models.CharField(max_length=10, choices=EntryType.choices)

    note = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shop} - {self.entry_type} - {self.amount}"
    