# apps/cart/models.py
from django.db import models


class Cart(models.Model):
    user       = models.OneToOneField(       # one cart per customer
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="cart",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart — {self.user.phone}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def item_count(self):
        return self.items.count()


class CartItem(models.Model):
    cart          = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product       = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
    )
    cut_type      = models.ForeignKey(
        "products.CutType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    quantity      = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
    )
    amount        = models.DecimalField(
        # customer says "Rs.200 worth" — we derive quantity from this
        max_digits=10, decimal_places=2,
        null=True, blank=True,
    )
    price_at_time = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0,
    )
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("cart", "product", "cut_type")

    def save(self, *args, **kwargs):
        # snapshot price at the moment item is added
        if not self.price_at_time:
            cut_extra = self.cut_type.extra_price if self.cut_type else 0
            self.price_at_time = self.product.effective_price + cut_extra

        # derive quantity from amount if customer ordered by price
        if self.amount and not self.quantity:
            self.quantity = self.amount / self.price_at_time

        # derive amount from quantity if customer ordered by weight
        if self.quantity and not self.amount:
            self.amount = self.quantity * self.price_at_time

        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        if self.quantity and self.price_at_time:
            return self.quantity * self.price_at_time
        return self.amount or 0

    def __str__(self):
        cut = f" ({self.cut_type.name})" if self.cut_type else ""
        return f"{self.product.name}{cut} x {self.quantity}"